from flask import Flask, request, jsonify, render_template, url_for, Response
from flask_cors import CORS
import sqlite3
import os
import json
from functools import wraps
app = Flask(__name__)
CORS(app)

DB_PATH = './data/crm.db'

# --- AUTHENTICATION ---

def check_auth(username, password):
    """Check username and password."""
    return username == 'admin' and password == 'admin123'

def authenticate():
    """Return a 401 Unauthorized response."""
    return Response(
        'Authentication required.', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

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

# --- ENDPOINT ---

@app.route('/api/smart-ivr', methods=['POST'])
def smart_ivr():
    # Support both JSON and Form data
    if request.is_json:
        data = request.get_json(silent=True)
    else:
        data = request.form.to_dict()
    
    if not data:
        data = {} # Ensure it's a dict for logging
    
    print(f"--- Incoming Request: {data}")
    
    caller = data.get('caller')
    
    # Default response for not found or invalid
    res = {"extension": "1094"}
    
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
                res = {"extension": "1093"}
                print(f"--- Yanıt (Kayıtlı ve Borcu Var): {res}")
            else:
                res = {"extension": "1094"}
                print(f"--- Yanıt (Kayıtlı ama Borcu Yok): {res}")
        else:
            print(f"--- Yanıt (Kayıt Bulunamadı): {res}")
    
    # Save log to database (Always logs every request now)
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
@requires_auth
def get_customers():
    conn = get_db_connection()
    customers = conn.execute('SELECT * FROM customers ORDER BY created_at DESC').fetchall()
    conn.close()
    return jsonify([dict(c) for c in customers])

# --- LOG APIs ---

@app.route('/api/logs', methods=['GET'])
@requires_auth
def get_logs():
    conn = get_db_connection()
    logs = conn.execute('SELECT * FROM logs ORDER BY timestamp DESC LIMIT 50').fetchall()
    conn.close()
    return jsonify([dict(l) for l in logs])

@app.route('/api/logs', methods=['DELETE'])
@requires_auth
def delete_logs():
    conn = get_db_connection()
    conn.execute('DELETE FROM logs')
    conn.commit()
    conn.close()
    return jsonify({"status": "success"}), 200

@app.route('/api/customers', methods=['POST'])
@requires_auth
def add_customer():
    data = request.json
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    phone = normalize_phone(data.get('phone'))
    email = data.get('email')
    company_name = data.get('company_name')
    has_debt = int(data.get('has_debt', 0)) # Default to 0
    
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
@requires_auth
def delete_customer(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM customers WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"}), 200

@app.route('/api/customers/<int:id>', methods=['PUT'])
@requires_auth
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
@requires_auth
def index():
    return render_template('index.html')

@app.route('/logs')
@requires_auth
def logs_page():
    return render_template('logs.html')

if __name__ == '__main__':
    # Ensure database exists
    if not os.path.exists(DB_PATH):
        from init_db import init_db
        init_db()
        
    port = int(os.environ.get('PORT', 5008))
    app.run(debug=True, host='0.0.0.0', port=port)
