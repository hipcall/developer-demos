from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_cors import CORS
import requests
import sqlite3
import os
import json
from dotenv import load_dotenv
from auth import login_required, check_credentials

load_dotenv()

app = Flask(__name__)
CORS(app)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-change-me')

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

HIPCALL_ACCOUNTS = json.loads(os.environ.get('HIPCALL_ACCOUNTS', '{}'))
DB_PATH = os.environ.get('DB_PATH', os.path.join(os.path.dirname(__file__), 'data', 'customers.db'))

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


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
        return render_template('login.html', error='Invalid username or password.', next=request.form.get('next', '/'))
    return render_template('login.html', error=None, next=request.args.get('next', '/'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# --- Frontend ---

@app.route('/')
@login_required
def index():
    accounts = [{"manage_id": k, "label": v.get("label", k)} for k, v in HIPCALL_ACCOUNTS.items()]
    return render_template('index.html', accounts=accounts)


# --- Customers API ---

@app.route('/api/customers', methods=['GET'])
@login_required
def get_customers():
    conn = get_db()
    customers = conn.execute('SELECT * FROM customers ORDER BY id DESC').fetchall()
    conn.close()
    return jsonify([dict(c) for c in customers])

@app.route('/api/customers', methods=['POST'])
@login_required
def add_customer():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    name = data.get('name', '').strip()
    department = data.get('department', '').strip()
    phone = data.get('phone', '').strip()

    if not all([name, department, phone]):
        return jsonify({"error": "All fields are required"}), 400

    conn = get_db()
    cursor = conn.execute(
        'INSERT INTO customers (name, department, phone) VALUES (?, ?, ?)',
        (name, department, phone)
    )
    conn.commit()
    inserted_id = cursor.lastrowid
    conn.close()

    return jsonify({"status": "success", "id": inserted_id}), 201

@app.route('/api/customers/<int:customer_id>', methods=['PUT'])
@login_required
def edit_customer(customer_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    name = data.get('name', '').strip()
    department = data.get('department', '').strip()
    phone = data.get('phone', '').strip()

    if not all([name, department, phone]):
        return jsonify({"error": "All fields are required"}), 400

    conn = get_db()
    conn.execute(
        'UPDATE customers SET name = ?, department = ?, phone = ? WHERE id = ?',
        (name, department, phone, customer_id)
    )
    conn.commit()
    conn.close()

    return jsonify({"status": "success"}), 200

@app.route('/api/customers/<int:customer_id>', methods=['DELETE'])
@login_required
def delete_customer(customer_id):
    conn = get_db()
    conn.execute('DELETE FROM customers WHERE id = ?', (customer_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"}), 200


# --- Call API ---

@app.route('/api/call', methods=['POST'])
@login_required
def make_call():
    data = request.get_json()
    if not data or 'callee_number' not in data:
        return jsonify({"error": "Missing 'callee_number' field"}), 400

    manage_id = data.get('manage_id', '')
    account = HIPCALL_ACCOUNTS.get(manage_id)
    if not account:
        return jsonify({"error": "Invalid or missing Hipcall account selection"}), 400

    api_key = account.get('api_key')
    user_id = str(data.get('user_id', '')).strip()
    if not user_id:
        return jsonify({"error": "Missing 'user_id' field"}), 400

    callee_number = data.get('callee_number').strip()
    if not callee_number.startswith('+'):
        if callee_number.startswith('0'):
            callee_number = '+90' + callee_number[1:]
        elif not callee_number.startswith('90'):
            callee_number = '+90' + callee_number
        else:
            callee_number = '+' + callee_number

    url = f"https://use.hipcall.com.tr/api/v3/users/{user_id}/call"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    payload = {
        "call_masking": True,
        "call_masking_name": "Support Team",
        "callee_number": callee_number,
        "ring_user_first": False
    }

    try:
        print(f"[DEBUG] Initiating call to: {url} | Payload: {payload}")
        response = requests.post(url, headers=headers, json=payload)
        print(f"[DEBUG] Hipcall API Response ({response.status_code}): {response.text}")

        if response.status_code == 201:
            return jsonify({
                "status": "success",
                "message": "Call initiated successfully",
                "hipcall_response": response.json()
            }), 201
        else:
            return jsonify({
                "error": "Failed to initiate call with Hipcall API",
                "status_code": response.status_code,
                "hipcall_response": response.json() if response.text else None
            }), response.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Request to Hipcall API failed: {str(e)}"}), 500


if __name__ == '__main__':
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    if not os.path.exists(DB_PATH):
        from init_db import init_db
        init_db()
    port = int(os.environ.get('PORT', 5011))
    app.run(debug=True, host='0.0.0.0', port=port)
