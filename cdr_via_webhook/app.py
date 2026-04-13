from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import sqlite3
import os
import json
import requests
import threading
import time

app = Flask(__name__)
CORS(app)

DB_PATH = './data/cdr_database.db'
RECORDS_DIR = './data/records'
DOWNLOAD_DELAY = 10  # Wait for the recording to be ready on storage

os.makedirs(RECORDS_DIR, exist_ok=True)


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def download_audio(record_url, uuid):
    """Download call recording from pre-signed URL after a short delay."""
    time.sleep(DOWNLOAD_DELAY)
    try:
        res = requests.get(record_url, stream=True, timeout=30)
        if res.status_code != 200:
            print(f"Failed to download audio for {uuid}: {res.status_code}")
            return

        local_path = os.path.join(RECORDS_DIR, f"{uuid}.mp3")
        with open(local_path, 'wb') as f:
            for chunk in res.iter_content(chunk_size=8192):
                f.write(chunk)

        conn = sqlite3.connect(DB_PATH)
        conn.execute('UPDATE cdrs SET local_record_path = ? WHERE uuid = ?',
                     (f"/api/records/{uuid}.mp3", uuid))
        conn.commit()
        conn.close()
        print(f"Downloaded audio for {uuid}")
    except Exception as e:
        print(f"Error downloading audio for {uuid}: {e}")


# --- Webhook ---

@app.route('/webhook/hipcall-cdr', methods=['POST'])
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

        record_url = data.get('record_url')
        if record_url:
            threading.Thread(target=download_audio, args=(record_url, uuid), daemon=True).start()

        return jsonify({"status": "success", "message": "CDR recorded"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- API ---

@app.route('/api/cdrs')
def get_cdrs():
    conn = get_db_connection()
    cdrs = conn.execute(
        'SELECT uuid, caller_number, callee_number, direction, duration, started_at, status '
        'FROM cdrs ORDER BY started_at DESC LIMIT 100'
    ).fetchall()
    conn.close()
    return jsonify([dict(c) for c in cdrs])


@app.route('/api/cdrs/<string:uuid>')
def get_cdr_details(uuid):
    conn = get_db_connection()
    cdr = conn.execute('SELECT * FROM cdrs WHERE uuid = ?', (uuid,)).fetchone()
    conn.close()
    if cdr:
        return jsonify(dict(cdr))
    return jsonify({"error": "CDR not found"}), 404


@app.route('/api/records/<filename>')
def get_audio_record(filename):
    return send_from_directory(RECORDS_DIR, filename)


# --- Frontend ---

@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5007))
    app.run(debug=True, host='0.0.0.0', port=port)
