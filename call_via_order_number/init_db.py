import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'orders.db')


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_code TEXT NOT NULL UNIQUE,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        phone TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        method TEXT,
        path TEXT,
        request_body TEXT,
        response_body TEXT,
        status_code INTEGER
    )
    ''')

    conn.commit()
    conn.close()
    print('Database initialized at', DB_PATH)


if __name__ == '__main__':
    init_db()
