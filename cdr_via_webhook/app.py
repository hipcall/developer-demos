from flask import Flask, request, jsonify, render_template, url_for
from flask_cors import CORS
import sqlite3
import os
import json

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

DB_PATH = './data/cdr_database.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# --- WEBHOOK ENDPOINT ---

@app.route('/webhook/hipcall-cdr', methods=['POST'])
def receive_cdr():
    payload = request.json
    if not payload:
        return jsonify({"error": "No payload received"}), 400
    
    # We are looking for call.ended or call_hangup events
    event_type = payload.get('event')
    data = payload.get('data', {})
    # We use call_hangup event here but you can also use other events for different purposes
    if event_type in ['call_hangup']:
        try:
            conn = get_db_connection()
            # Check if this uuid already exists to avoid duplicates
            existing = conn.execute('SELECT uuid FROM cdrs WHERE uuid = ?', (data.get('uuid'),)).fetchone()
            
            if not existing:
                conn.execute('''
                    INSERT INTO cdrs (
                        uuid, caller_number, callee_number, direction, 
                        duration, status, started_at, ended_at, record_url, 
                        hangup_by, raw_payload
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    data.get('uuid'),
                    data.get('caller_number'),
                    data.get('callee_number'),
                    data.get('direction'),
                    data.get('call_duration'),
                    'completed',
                    data.get('started_at'),
                    data.get('ended_at'),
                    data.get('record_url'), #This is an expired URL, you need to download the file and store it in your own datastore for production environments.  
                    data.get('hangup_by'),
                    json.dumps(payload)
                ))
                conn.commit()
                conn.close()
                return jsonify({"status": "success", "message": "CDR recorded"}), 201
            else:
                conn.close()
                return jsonify({"status": "exists", "message": "CDR already exists"}), 200
        except Exception as e:
            if 'conn' in locals(): conn.close()
            return jsonify({"error": str(e)}), 500
            
    return jsonify({"status": "ignored", "message": f"Event type {event_type} ignored"}), 200

# --- API ENDPOINTS ---

@app.route('/api/cdrs', methods=['GET'])
def get_cdrs():
    conn = get_db_connection()
    cdrs = conn.execute('SELECT uuid, caller_number, callee_number, direction, duration, started_at, status FROM cdrs ORDER BY started_at DESC LIMIT 100').fetchall()
    conn.close()
    return jsonify([dict(c) for c in cdrs])

@app.route('/api/cdrs/<string:uuid>', methods=['GET'])
def get_cdr_details(uuid):
    conn = get_db_connection()
    cdr = conn.execute('SELECT * FROM cdrs WHERE uuid = ?', (uuid,)).fetchone()
    conn.close()
    if cdr:
        return jsonify(dict(cdr))
    return jsonify({"error": "CDR not found"}), 404

# --- FRONTEND ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5007))
    app.run(debug=True, host='0.0.0.0', port=port)
