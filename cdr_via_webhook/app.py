from flask import Flask, request, jsonify, render_template, Response, session, redirect, url_for
from flask_cors import CORS
import sqlite3
import os
import json
import requests
from dotenv import load_dotenv
from auth import login_required, check_credentials

load_dotenv()

app = Flask(__name__)
CORS(app)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-change-me')

DB_PATH = os.environ.get('DB_PATH', os.path.join(os.path.dirname(__file__), 'data', 'cdr_database.db'))
HIPCALL_ACCOUNTS = json.loads(os.environ.get('HIPCALL_ACCOUNTS', '{}'))
HIPCALL_BASE_URL = 'https://use.hipcall.com.tr'

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


def get_db_connection():
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
        return render_template('login.html', error='Invalid username or password.', next=request.form.get('next') or url_for('index'))
    return render_template('login.html', error=None, next=request.args.get('next') or url_for('index'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# --- Webhook ---

@app.route('/api/hipcall-cdr', methods=['POST'])
def receive_cdr():
    payload = request.json
    if not payload:
        return jsonify({"error": "No payload received"}), 400

    event_type = payload.get('event')
    if event_type != 'call_hangup':
        return jsonify({"status": "ignored", "message": f"Event '{event_type}' ignored"}), 200

    data = payload.get('data', {})
    uuid = data.get('uuid')

    try:
        conn = get_db_connection()
        if conn.execute('SELECT 1 FROM cdrs WHERE uuid = ?', (uuid,)).fetchone():
            conn.close()
            return jsonify({"status": "exists", "message": "CDR already exists"}), 200

        conn.execute('''
            INSERT INTO cdrs (uuid, caller_number, callee_number, direction,
                              duration, status, started_at, ended_at,
                              record_url, hangup_by, raw_payload)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            uuid,
            data.get('caller_number'),
            data.get('callee_number'),
            data.get('direction'),
            data.get('call_duration'),
            'completed',
            data.get('started_at'),
            data.get('ended_at'),
            data.get('record_url'),
            data.get('hangup_by'),
            json.dumps(payload)
        ))
        conn.commit()
        conn.close()

        return jsonify({"status": "success", "message": "CDR recorded"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- API ---

@app.route('/api/cdrs', methods=['DELETE'])
@login_required
def clear_cdrs():
    conn = get_db_connection()
    conn.execute('DELETE FROM cdrs')
    conn.commit()
    conn.close()
    return jsonify({"status": "success"}), 200


@app.route('/api/cdrs')
@login_required
def get_cdrs():
    conn = get_db_connection()
    cdrs = conn.execute(
        'SELECT uuid, caller_number, callee_number, direction, duration, started_at, status '
        'FROM cdrs ORDER BY started_at DESC LIMIT 100'
    ).fetchall()
    conn.close()
    return jsonify([dict(c) for c in cdrs])


@app.route('/api/cdrs/<string:uuid>')
@login_required
def get_cdr_details(uuid):
    conn = get_db_connection()
    cdr = conn.execute('SELECT * FROM cdrs WHERE uuid = ?', (uuid,)).fetchone()
    conn.close()
    if cdr:
        return jsonify(dict(cdr))
    return jsonify({"error": "CDR not found"}), 404


@app.route('/api/records/<string:uuid>')
@login_required
def get_audio_record(uuid):
    account_id = request.args.get('account_id', '')
    account = HIPCALL_ACCOUNTS.get(account_id)
    if not account:
        return jsonify({"error": "Please select a valid Hipcall account"}), 400

    api_key = account.get('api_key', '')

    conn = get_db_connection()
    row = conn.execute('SELECT started_at FROM cdrs WHERE uuid = ?', (uuid,)).fetchone()
    conn.close()

    if not row or not row['started_at']:
        return jsonify({"error": "CDR not found"}), 404

    call_date = row['started_at'][:10]

    try:
        api_resp = requests.get(
            f"{HIPCALL_BASE_URL}/api/v3/calls/{uuid}",
            params={"date": call_date},
            headers={
                "Authorization": f"Bearer {api_key}",
                "Accept": "application/json"
            },
            timeout=10
        )
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Hipcall API request failed: {str(e)}"}), 502

    if api_resp.status_code != 200:
        return jsonify({"error": "Recording not available", "detail": api_resp.text}), 404

    record_url = api_resp.json().get('data', {}).get('record_url')
    if not record_url:
        return jsonify({"error": "No recording for this call"}), 404

    if record_url.startswith('/'):
        record_url = HIPCALL_BASE_URL + record_url

    try:
        audio_resp = requests.get(
            record_url,
            headers={"Authorization": f"Bearer {api_key}"},
            stream=True,
            timeout=30
        )
        if audio_resp.status_code != 200:
            return jsonify({"error": "Failed to fetch recording audio"}), 404

        return Response(
            audio_resp.iter_content(chunk_size=8192),
            content_type=audio_resp.headers.get('Content-Type', 'audio/mpeg'),
            status=200
        )
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to stream audio: {str(e)}"}), 502


# --- Frontend ---

@app.route('/')
@login_required
def index():
    accounts = [{"account_id": k, "label": v.get("label", k)} for k, v in HIPCALL_ACCOUNTS.items()]
    return render_template('index.html', accounts=accounts)


if __name__ == '__main__':
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    from init_db import init_db
    init_db()
    port = int(os.environ.get('PORT', 5007))
    app.run(debug=True, host='0.0.0.0', port=port)
