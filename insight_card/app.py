from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
import os
import json
import requests as http_requests

app = Flask(__name__)
CORS(app)

DB_PATH = './data/insight_card.db'
HIPCALL_API_URL = 'https://use.hipcall.com.tr/api/v3'
HIPCALL_API_TOKEN = os.environ.get('HIPCALL_API_TOKEN', '')


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def normalize_phone(phone):
    """Normalize phone to E.164 format (90532...)."""
    if not phone:
        return ''
    # Strip non-digits except '+'
    digits = ''.join(c for c in phone if c.isdigit() or c == '+')
    # Remove leading '+'
    digits = digits.lstrip('+')
    # If it starts with '0', replace with '90' (Turkey specific assumption, but common for this user)
    # However, Hipcall usually sends 90... directly.
    # We should match what's in the DB.
    if digits.startswith('0'):
        digits = '90' + digits[1:]
    return digits


def find_contact(phone):
    normalized = normalize_phone(phone)
    conn = get_db()
    contact = conn.execute(
        'SELECT * FROM contacts WHERE phone_number = ?', (normalized,)
    ).fetchone()
    conn.close()
    return dict(contact) if contact else None


def send_card(call_id, contact):
    headers = {
        'Authorization': f'Bearer {HIPCALL_API_TOKEN}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    payload = {
        "card": [
            {"type": "title", "text": "Hipcall Insight", "link": "https://www.hipcall.com.tr"},
            {"type": "shortText", "label": "Ad Soyad", "text": contact['full_name']},
            {"type": "shortText", "label": "Kurumsal", "text": contact['company']},
            {"type": "shortText", "label": "Bakiye", "text": f"{contact['balance']} TL"}
        ]
    }

    url = f'{HIPCALL_API_URL}/calls/{call_id}/cards'
    print(f"[REQUEST] POST {url} | Body: {json.dumps(payload)}")

    try:
        resp = http_requests.post(url, json=payload, headers=headers, timeout=10)
        print(f"[RESPONSE] {resp.status_code}: {resp.text}")
        return resp.status_code
    except Exception as e:
        print(f"Card API error: {e}")
        return 0


# --- Webhook ---

@app.route('/webhook/insight-card', methods=['POST'])
def webhook():
    payload = request.json
    if not payload:
        return jsonify({"error": "No payload"}), 400

    event = payload.get('event')
    if event != 'call_init':
        return jsonify({"status": "ignored", "event": event}), 200

    data = payload.get('data', {})
    call_id = data.get('uuid')
    direction = data.get('direction')

    # outbound -> customer is callee, inbound -> customer is caller
    customer_number = data.get('callee_number', '') if direction == 'outbound' else data.get('caller_number', '')

    contact = find_contact(customer_number)
    if not contact:
        return jsonify({"status": "no_match", "customer_number": customer_number}), 200

    code = send_card(call_id, contact)
    status = 'sent' if code in (200, 201) else 'failed'
    matched_number = contact['phone_number']

    conn = get_db()
    conn.execute(
        'INSERT INTO card_logs (call_id, caller_number, contact_name, contact_company, status, response_code, raw_payload) VALUES (?,?,?,?,?,?,?)',
        (call_id, matched_number, contact['full_name'], contact['company'], status, code, json.dumps(payload))
    )
    conn.commit()
    conn.close()

    return jsonify({"status": status, "contact": contact['full_name']}), 201


# --- API ---

@app.route('/api/contacts')
def get_contacts():
    conn = get_db()
    contacts = conn.execute('SELECT * FROM contacts ORDER BY full_name').fetchall()
    conn.close()
    return jsonify([dict(c) for c in contacts])


@app.route('/api/contacts', methods=['POST'])
def add_contact():
    data = request.json
    if not data or not data.get('phone_number') or not data.get('full_name') or not data.get('company'):
        return jsonify({"error": "Fields phone_number, full_name, and company are required"}), 400

    phone = normalize_phone(data['phone_number'])
    balance = data.get('balance', '0.00')
    conn = get_db()
    try:
        conn.execute('INSERT INTO contacts (phone_number, full_name, company, balance) VALUES (?,?,?,?)',
                     (phone, data['full_name'], data['company'], balance))
        conn.commit()
        conn.close()
        return jsonify({"status": "created"}), 201
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "Phone number already exists"}), 409


@app.route('/api/contacts/<int:contact_id>', methods=['PUT'])
def update_contact(contact_id):
    data = request.json
    if not data:
        return jsonify({"error": "No data"}), 400

    conn = get_db()
    contact = conn.execute('SELECT * FROM contacts WHERE id = ?', (contact_id,)).fetchone()
    if not contact:
        conn.close()
        return jsonify({"error": "Contact not found"}), 404

    phone = data.get('phone_number', contact['phone_number'])
    name = data.get('full_name', contact['full_name'])
    company = data.get('company', contact['company'])
    balance = data.get('balance', contact['balance'])

    try:
        conn.execute('UPDATE contacts SET phone_number=?, full_name=?, company=?, balance=? WHERE id=?',
                     (normalize_phone(phone), name, company, balance, contact_id))
        conn.commit()
        conn.close()
        return jsonify({"status": "updated"})
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "Phone number already exists"}), 409


@app.route('/api/contacts/<int:contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
    conn = get_db()
    conn.execute('DELETE FROM contacts WHERE id = ?', (contact_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "deleted"})


@app.route('/api/logs')
def get_logs():
    conn = get_db()
    logs = conn.execute('SELECT * FROM card_logs ORDER BY created_at DESC LIMIT 50').fetchall()
    conn.close()
    return jsonify([dict(l) for l in logs])


# --- Frontend ---

@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5009))
    app.run(debug=True, host='0.0.0.0', port=port)
