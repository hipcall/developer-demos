from flask import Flask, request, jsonify, render_template, session, redirect, url_for, Response
from flask_cors import CORS
import sqlite3
import os
import json
from auth import login_required, check_credentials

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

DB_PATH = os.environ.get('DB_PATH', './data/crm.db')
EXTENSION_DEBT = os.environ.get('EXTENSION_DEBT')
EXTENSION_NO_DEBT = os.environ.get('EXTENSION_NO_DEBT')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def normalize_phone(phone):
    """Normalize phone number to match the database format (e.g., 905438851111)"""
    if not phone:
        return ""
    # Remove non-numeric characters
    phone = ''.join(filter(str.isdigit, phone))
    # Handle Turkish numbers
    if phone.startswith('0') and len(phone) == 11:
        phone = '9' + phone
    elif len(phone) == 10:
        phone = '90' + phone
    return phone

# --- AUTH ---

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


# --- ENDPOINT ---

@app.route('/api/smart-ivr', methods=['POST'])
def smart_ivr():
    # Support both JSON and Form data
    if request.is_json:
        data = request.get_json(silent=True)
    else:
        data = request.form.to_dict()

    if not data:
        data = {}

    print(f"--- Incoming Request: {data}")

    caller = data.get('caller')

    # Default response for not found or invalid
    res = {"extension": EXTENSION_NO_DEBT}

    if not caller:
        print(f"--- Yanıt (Caller Yok veya Veri Yok): {res}")
    else:
        normalized_caller = normalize_phone(caller)

        conn = get_db_connection()
        customer = conn.execute(
            'SELECT id, has_debt FROM customers WHERE phone = ?',
            (normalized_caller,)
        ).fetchone()
        conn.close()

        if customer:
            if customer['has_debt'] == 1:
                res = {"extension": EXTENSION_DEBT}
                print(f"--- Yanıt (Kayıtlı ve Borcu Var): {res}")
            else:
                res = {"extension": EXTENSION_NO_DEBT}
                print(f"--- Yanıt (Kayıtlı ama Borcu Yok): {res}")
        else:
            print(f"--- Yanıt (Kayıt Bulunamadı): {res}")

    # Save log to database
    try:
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO logs (request_body, response_body) VALUES (?, ?)',
            (json.dumps(data), json.dumps(res))
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Logging error: {e}")

    return jsonify(res), 200

# --- CRM APIs ---

@app.route('/api/customers', methods=['GET'])
@login_required
def get_customers():
    conn = get_db_connection()
    customers = conn.execute('SELECT * FROM customers ORDER BY created_at DESC').fetchall()
    conn.close()
    return jsonify([dict(c) for c in customers])

# --- LOG APIs ---

@app.route('/api/logs', methods=['GET'])
@login_required
def get_logs():
    conn = get_db_connection()
    logs = conn.execute('SELECT * FROM logs ORDER BY timestamp DESC LIMIT 50').fetchall()
    conn.close()
    return jsonify([dict(l) for l in logs])

@app.route('/api/logs', methods=['DELETE'])
@login_required
def delete_logs():
    conn = get_db_connection()
    conn.execute('DELETE FROM logs')
    conn.commit()
    conn.close()
    return jsonify({"status": "success"}), 200

@app.route('/api/customers', methods=['POST'])
@login_required
def add_customer():
    data = request.json
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    phone = normalize_phone(data.get('phone'))
    email = data.get('email')
    company_name = data.get('company_name')
    has_debt = int(data.get('has_debt', 0))

    if not first_name or not last_name or not phone:
        return jsonify({"error": "Missing required fields"}), 400

    try:
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO customers (first_name, last_name, phone, email, company_name, has_debt) VALUES (?, ?, ?, ?, ?, ?)',
            (first_name, last_name, phone, email, company_name, has_debt)
        )
        conn.commit()
        conn.close()
        return jsonify({"status": "success"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Phone number already exists"}), 400

@app.route('/api/customers/<int:id>', methods=['DELETE'])
@login_required
def delete_customer(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM customers WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"}), 200

@app.route('/api/customers/<int:id>', methods=['PUT'])
@login_required
def update_customer(id):
    data = request.json
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    phone = normalize_phone(data.get('phone'))
    email = data.get('email')
    company_name = data.get('company_name')
    has_debt = int(data.get('has_debt', 0))

    if not first_name or not last_name or not phone:
        return jsonify({"error": "Missing required fields"}), 400

    try:
        conn = get_db_connection()
        conn.execute(
            'UPDATE customers SET first_name=?, last_name=?, phone=?, email=?, company_name=?, has_debt=? WHERE id=?',
            (first_name, last_name, phone, email, company_name, has_debt, id)
        )
        conn.commit()
        conn.close()
        return jsonify({"status": "success"}), 200
    except sqlite3.IntegrityError:
        return jsonify({"error": "Phone number already exists"}), 400

# --- FRONTEND ROUTES ---

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/logs')
@login_required
def logs_page():
    return render_template('logs.html')

if __name__ == '__main__':
    if not os.path.exists(DB_PATH):
        from init_db import init_db
        init_db()

    port = int(os.environ.get('PORT', 5008))
    app.run(debug=True, host='0.0.0.0', port=port)
