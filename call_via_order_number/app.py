from flask import Flask, request, jsonify, render_template, session, redirect, url_for
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

DB_PATH = os.environ.get('DB_PATH', os.path.join(os.path.dirname(__file__), 'data', 'orders.db'))


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def normalize_phone(phone):
    phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    if phone.startswith('+'):
        phone = phone[1:]
    if phone.startswith('90') and len(phone) == 12:
        return phone
    if phone.startswith('0') and len(phone) == 11:
        return '90' + phone[1:]
    if len(phone) == 10 and not phone.startswith('0'):
        return '90' + phone
    return phone


def log_request(method, path, req_body, res_body, status_code):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            'INSERT INTO logs (method, path, request_body, response_body, status_code) '
            'VALUES (?, ?, ?, ?, ?)',
            (method, path, req_body, res_body, status_code)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Logging error: {e}")


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


# --- Hipcall Speed Dial Endpoint ---

@app.route('/lookup', methods=['POST'])
def lookup():
    data = request.get_json()
    req_body = json.dumps(data) if data else ''

    if not data or 'number' not in data:
        res = {"error": "Missing 'number' field"}
        log_request('POST', '/lookup', req_body, json.dumps(res), 400)
        return jsonify(res), 400

    code = str(data['number']).strip()

    if not code.isdigit() or len(code) != 4:
        res = {"error": "Invalid reference code. Must be exactly 4 digits."}
        log_request('POST', '/lookup', req_body, json.dumps(res), 400)
        return jsonify(res), 400

    conn = get_db()
    row = conn.execute(
        'SELECT phone FROM orders WHERE order_code = ?', (code,)
    ).fetchone()
    conn.close()

    if row:
        res = {"destination": row['phone']}
        log_request('POST', '/lookup', req_body, json.dumps(res), 200)
        return jsonify(res), 200
    else:
        res = {"error": "Reference code not found"}
        log_request('POST', '/lookup', req_body, json.dumps(res), 404)
        return jsonify(res), 404


# --- Order Management API ---

@app.route('/api/orders', methods=['GET'])
@login_required
def get_orders():
    conn = get_db()
    orders = conn.execute(
        'SELECT * FROM orders ORDER BY created_at DESC'
    ).fetchall()
    conn.close()
    return jsonify([dict(o) for o in orders])


@app.route('/api/orders', methods=['POST'])
@login_required
def create_order():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    order_code = data.get('order_code', '').strip()
    first_name = data.get('first_name', '').strip()
    last_name = data.get('last_name', '').strip()
    phone = data.get('phone', '').strip()

    if not all([order_code, first_name, last_name, phone]):
        return jsonify({"error": "All fields are required"}), 400

    if not order_code.isdigit() or len(order_code) != 4:
        return jsonify({"error": "Reference code must be exactly 4 digits"}), 400

    phone = normalize_phone(phone)

    try:
        conn = get_db()
        conn.execute(
            'INSERT INTO orders (order_code, first_name, last_name, phone) VALUES (?, ?, ?, ?)',
            (order_code, first_name, last_name, phone)
        )
        conn.commit()
        conn.close()
        return jsonify({"status": "success"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Reference code already exists"}), 409


@app.route('/api/orders/<int:order_id>', methods=['DELETE'])
@login_required
def delete_order(order_id):
    conn = get_db()
    conn.execute('DELETE FROM orders WHERE id = ?', (order_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})


# --- Logs API ---

@app.route('/api/logs', methods=['GET'])
@login_required
def get_logs():
    conn = get_db()
    logs = conn.execute(
        'SELECT * FROM logs ORDER BY id DESC LIMIT 50'
    ).fetchall()
    conn.close()
    return jsonify([dict(l) for l in logs])


@app.route('/api/logs', methods=['DELETE'])
@login_required
def clear_logs():
    conn = get_db()
    conn.execute('DELETE FROM logs')
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})


# --- Frontend Routes ---

@app.route('/')
@login_required
def index():
    return render_template('index.html')


@app.route('/logs')
@login_required
def logs_page():
    return render_template('logs.html')


if __name__ == '__main__':
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    if not os.path.exists(DB_PATH):
        from init_db import init_db
        init_db()
    port = int(os.environ.get('PORT', 5010))
    app.run(debug=True, host='0.0.0.0', port=port)
