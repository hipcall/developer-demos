import sqlite3
import os

DB_PATH = './data/cdr_database.db'

def init_db():
    # Ensure data directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create CDRs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cdrs (
            uuid TEXT PRIMARY KEY,
            caller_number TEXT,
            callee_number TEXT,
            direction TEXT,
            duration INTEGER,
            status TEXT,
            started_at TEXT,
            ended_at TEXT,
            record_url TEXT,
            hangup_by TEXT,
            raw_payload TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

if __name__ == '__main__':
    init_db()
