from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_cors import CORS
import sqlite3
import os
import json
from auth import login_required, check_credentials

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-change-me')

_script_name = os.environ.get('SCRIPT_NAME', '')
if _script_name:
    class _ScriptNameMiddleware:
        def __init__(self, wsgi_app, script_name):
            self.wsgi_app = wsgi_app
            self.script_name = script_name
        def __call__(self, environ, start_response):
            environ['SCRIPT_NAME'] = self.script_name
            return self.wsgi_app(environ, start_response)
    app.wsgi_app = _ScriptNameMiddleware(app.wsgi_app, _script_name)

DB_PATH = os.environ.get('DB_PATH', './data/database.db')
PUBLIC_BASE_URL = os.environ.get('PUBLIC_BASE_URL', '')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def normalize_phone(phone):
    if not phone:
        return phone
    phone = phone.strip()
    if phone.startswith('+90'):
        phone = phone[3:]
    elif phone.startswith('90') and len(phone) == 12:
        phone = phone[2:]
    elif phone.startswith('0') and len(phone) == 11:
        phone = phone[1:]
    return phone

def number_to_turkish_words(n):
    if n is None:
        return "sıfır lira"
    try:
        n = float(n)
    except ValueError:
        return "sıfır lira"
        
    ones = ["", "bir", "iki", "üç", "dört", "beş", "altı", "yedi", "sekiz", "dokuz"]
    tens = ["", "on", "yirmi", "otuz", "kırk", "elli", "altmış", "yetmiş", "seksen", "doksan"]
    
    def read_triplet(num):
        res = []
        h = num // 100
        t = (num % 100) // 10
        o = num % 10
        
        if h == 1:
            res.append("yüz")
        elif h > 1:
            res.append(ones[h] + " yüz")
        
        if t > 0:
            res.append(tens[t])
            
        if o > 0:
            res.append(ones[o])
            
        return " ".join(res)
        
    int_part = int(n)
    frac_part = round((n - int_part) * 100)
    
    parts = []
    
    if int_part == 0:
        parts.append("sıfır")
    else:
        b = int_part // 1000000000
        m = (int_part % 1000000000) // 1000000
        k = (int_part % 1000000) // 1000
        r = int_part % 1000
        
        if b > 0:
            parts.append(read_triplet(b) + " milyar")
        if m > 0:
            parts.append(read_triplet(m) + " milyon")
        if k == 1:
            parts.append("bin")
        elif k > 1:
            parts.append(read_triplet(k) + " bin")
        if r > 0:
            parts.append(read_triplet(r))
            
    # Temizleme
    text = " ".join([p for p in " ".join(parts).split() if p]) + " lira"
    
    if frac_part > 0:
        frac_text = " ".join([p for p in read_triplet(frac_part).split() if p])
        text += f" {frac_text} kuruş"
        
    return text.strip()

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


# --- USER MANAGEMENT APIs ---

@app.route('/api/users', methods=['GET'])
@login_required
def get_users():
    conn = get_db_connection()
    users = conn.execute('SELECT id, first_name, last_name, phone, pin_code, balance FROM users').fetchall()
    conn.close()
    return jsonify([dict(u) for u in users])

@app.route('/api/users', methods=['POST'])
@login_required
def add_user():
    data = request.json
    conn = get_db_connection()
    phone = normalize_phone(data.get('phone'))
    
    balance = data.get('balance')
    if balance == '' or balance is None:
        balance = 0.0
        
    conn.execute("""INSERT INTO users (first_name, last_name, phone, pin_code, balance) 
                    VALUES (?, ?, ?, ?, ?)""", 
                 (data.get('first_name'), data.get('last_name'), phone, data.get('pin_code'), balance))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/api/users/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    data = request.json
    conn = get_db_connection()
    phone = normalize_phone(data.get('phone'))
    
    balance = data.get('balance')
    if balance == '' or balance is None:
        balance = 0.0
        
    conn.execute("""UPDATE users SET first_name=?, last_name=?, phone=?, pin_code=?, balance=? 
                    WHERE id=?""", 
                 (data.get('first_name'), data.get('last_name'), phone, data.get('pin_code'), balance, user_id))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM users WHERE id=?', (user_id,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

# --- LOGGING ---

@app.after_request
def log_request_response(response):
    # Sadece Hipcall Ingress isteklerini logla
    if request.path == '/api/external/hipcall-ingress':
        try:
            req_body = request.get_data(as_text=True)
            res_body = response.get_data(as_text=True)
            
            # Truncate body if too large or binary
            if len(req_body) > 5000: req_body = "Body too large"
            if len(res_body) > 5000: res_body = "Body too large"

            conn = get_db_connection()
            conn.execute(
                "INSERT INTO logs (method, path, request_body, response_body) VALUES (?, ?, ?, ?)",
                (request.method, request.path, req_body, res_body)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Logging error: {e}")
            
    return response

@app.route('/api/logs', methods=['GET'])
@login_required
def get_logs():
    conn = get_db_connection()
    logs = conn.execute("SELECT id, timestamp, method, path, request_body, response_body FROM logs ORDER BY id DESC LIMIT 50").fetchall()
    conn.close()
    return jsonify([dict(l) for l in logs])

@app.route('/api/logs', methods=['DELETE'])
@login_required
def delete_logs():
    conn = get_db_connection()
    conn.execute("DELETE FROM logs")
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

# --- HIPCALL EXTERNAL MANAGEMENT INGRESS ---

@app.route('/api/external/hipcall-ingress', methods=['POST'])
def hipcall_ingress():
    data = request.json
    caller = data.get('caller')
    gather_data = data.get('data', {})

    conn = get_db_connection()
    normalized_caller = normalize_phone(caller)
    user = conn.execute(
        'SELECT * FROM users WHERE phone = ?', 
        (normalized_caller,)
    ).fetchone()
    conn.close()

    entered_pin = gather_data.get('pin_code')

    # If the call just started, ask for PIN
    if 'pin_code' not in gather_data:
        return jsonify({
            "version": "1.0",
            "seq": [
                {
                    "action": "gather",
                    "args": {
                        "min_digits": 1,
                        "max_digits": 4,
                        "ask": f"{PUBLIC_BASE_URL}/static/audio/pin_karsilama.mp3",
                        "variable_name": "pin_code"
                    }
                }
            ]
        })

    # If PIN was entered, verify it
    if user and entered_pin == user['pin_code']:
        balance_text = number_to_turkish_words(user['balance'])
        return jsonify({
            "version": "1.0",
            "seq": [
                {
                    "action": "say",
                    "args": {
                        "text": f"Hoşgeldiniz {user['first_name']} {user['last_name']}. Şu anda {balance_text} bakiyeniz bulunmaktadır. Sizi satış temsilcisine aktarıyorum.",
                        "language": "tr-TR"
                    }
                },
                {
                    "action": "connect",
                    "args": {
                        "destination": "801"
                    }
                }
            ]
        })
    else:
        return jsonify({
            "version": "1.0",
            "seq": [
                {
                    "action": "play",
                    "args": {
                        "url": f"{PUBLIC_BASE_URL}/static/audio/pin_basarisiz1.mp3"
                    }
                },
                {
                    "action": "connect",
                    "args": {
                        "destination": "802"
                    }
                }
            ]
        })

# --- FRONTEND ROUTE ---

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/logs')
@login_required
def logs():
    return render_template('logs.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5005))
    app.run(debug=True, host='0.0.0.0', port=port)
