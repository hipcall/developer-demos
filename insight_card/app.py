from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_cors import CORS
import sqlite3
import os
import json
import requests as http_requests
from dotenv import load_dotenv
from auth import login_required, check_credentials

load_dotenv()

app = Flask(__name__)
CORS(app)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-change-me')

DB_PATH = os.environ.get('DB_PATH', os.path.join(os.path.dirname(__file__), 'data', 'insight_card.db'))
HIPCALL_API_URL = 'https://use.hipcall.com.tr/api/v3'
HIPCALL_ACCOUNTS = json.loads(os.environ.get('HIPCALL_ACCOUNTS', '{}'))

_script_name = os.environ.get('APP_SCRIPT_NAME', '')
if _script_name:
    class _ScriptNameMiddleware:
        def __init__(self, wsgi_app, script_name):
            self.wsgi_app = wsgi_app
            self.script_name = script_name
        def __call__(self, environ, start_response):
            environ['SCRIPT_NAME'] = self.script_name
            return self.wsgi_app(environ, start_response)
    app.wsgi_app = _ScriptNameMiddleware(app.wsgi_app, _script_name)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_active_api_key():
    conn = get_db()
    row = conn.execute("SELECT value FROM settings WHERE key = 'active_account'").fetchone()
    conn.close()
    if not row:
        return None
    account = HIPCALL_ACCOUNTS.get(row['value'])
    return account.get('api_key') if account else None


def normalize_phone(phone):
    if not phone:
        return ''
    digits = ''.join(c for c in phone if c.isdigit() or c == '+')
    digits = digits.lstrip('+')
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


def send_card(call_id, contact, api_key):
    headers = {
        'Authorization': f'Bearer {api_key}',
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


# --- Auth ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if check_credentials(username, password):
            session['logged_in'] = True
            next_url = request.form.get('next') or url_for('index')
            return redirect(next_url)
        return render_template('login.html', error='Invalid username or password.', next=request.form.get('next') or url_for('index'))
    return render_template('login.html', error=None, next=request.args.get('next') or url_for('index'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# --- Webhook ---

@app.route('/webhook/insight-card', methods=['POST'])
def webhook():
    payload = request.json
    if not payload:
        return jsonify({"error": "No payload"}), 400

    event = payload.get('event')
    if event != 'call_init':
        return jsonify({"status": "ignored", "event": event}), 200

    api_key = get_active_api_key()
    if not api_key:
        return jsonify({"error": "No active Hipcall account configured"}), 503

    data = payload.get('data', {})
    call_id = data.get('uuid')
    direction = data.get('direction')

    customer_number = data.get('callee_number', '') if direction == 'outbound' else data.get('caller_number', '')

    contact = find_contact(customer_number)
    if not contact:
        return jsonify({"status": "no_match", "customer_number": customer_number}), 200

    code = send_card(call_id, contact, api_key)
    status = 'sent' if code in (200, 201) else 'failed'

    conn = get_db()
    conn.execute(
        'INSERT INTO card_logs (call_id, caller_number, contact_name, contact_company, status, response_code, raw_payload) VALUES (?,?,?,?,?,?,?)',
        (call_id, contact['phone_number'], contact['full_name'], contact['company'], status, code, json.dumps(payload))
    )
    conn.commit()
    conn.close()

    return jsonify({"status": status, "contact": contact['full_name']}), 201


# --- Settings API ---

@app.route('/api/settings/active-account', methods=['GET'])
@login_required
def get_active_account():
    conn = get_db()
    row = conn.execute("SELECT value FROM settings WHERE key = 'active_account'").fetchone()
    conn.close()
    return jsonify({"active_account": row['value'] if row else None})


@app.route('/api/settings/active-account', methods=['POST'])
@login_required
def set_active_account():
    data = request.get_json()
    account_id = data.get('account_id', '')
    if account_id and account_id not in HIPCALL_ACCOUNTS:
        return jsonify({"error": "Invalid account"}), 400
    conn = get_db()
    conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('active_account', ?)", (account_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})


# --- Contacts API ---

@app.route('/api/contacts')
@login_required
def get_contacts():
    conn = get_db()
    contacts = conn.execute('SELECT * FROM contacts ORDER BY full_name').fetchall()
    conn.close()
    return jsonify([dict(c) for c in contacts])


@app.route('/api/contacts', methods=['POST'])
@login_required
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
@login_required
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
@login_required
def delete_contact(contact_id):
    conn = get_db()
    conn.execute('DELETE FROM contacts WHERE id = ?', (contact_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "deleted"})


@app.route('/api/logs')
@login_required
def get_logs():
    conn = get_db()
    logs = conn.execute('SELECT * FROM card_logs ORDER BY created_at DESC LIMIT 50').fetchall()
    conn.close()
    return jsonify([dict(l) for l in logs])


# --- Frontend ---

@app.route('/')
@login_required
def index():
    accounts = [{"account_id": k, "label": v.get("label", k)} for k, v in HIPCALL_ACCOUNTS.items()]
    return render_template('index.html', accounts=accounts)


if __name__ == '__main__':
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    port = int(os.environ.get('PORT', 5009))
    app.run(debug=True, host='0.0.0.0', port=port)
