from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

HIPCALL_API_KEY = os.environ.get('HIPCALL_API_KEY')
HIPCALL_USER_ID = "3508"
DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'customers.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

# --- Customers API ---

@app.route('/api/customers', methods=['GET'])
def get_customers():
    conn = get_db()
    customers = conn.execute('SELECT * FROM customers ORDER BY id DESC').fetchall()
    conn.close()
    return jsonify([dict(c) for c in customers])

@app.route('/api/customers', methods=['POST'])
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
def delete_customer(customer_id):
    conn = get_db()
    conn.execute('DELETE FROM customers WHERE id = ?', (customer_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"}), 200


# --- Call API ---

@app.route('/api/call', methods=['POST'])
def make_call():
    if not HIPCALL_API_KEY:
        return jsonify({"error": "Server configuration missing (API Key)"}), 500

    data = request.get_json()
    if not data or 'callee_number' not in data:
        return jsonify({"error": "Missing 'callee_number' field"}), 400

    callee_number = data.get('callee_number').strip()
    if not callee_number.startswith('+'):
        if callee_number.startswith('0'):
            callee_number = '+90' + callee_number[1:]
        elif not callee_number.startswith('90'):
            callee_number = '+90' + callee_number
        else:
            callee_number = '+' + callee_number

    url = f"https://use.hipcall.com.tr/api/v3/users/{HIPCALL_USER_ID}/call"
    
    headers = {
        "Authorization": f"Bearer {HIPCALL_API_KEY}",
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
