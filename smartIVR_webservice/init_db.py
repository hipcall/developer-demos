import sqlite3
import os

DB_PATH = './data/crm.db'

def init_db():
    if not os.path.exists('./data'):
        os.makedirs('./data')
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create customers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        phone TEXT NOT NULL UNIQUE,
        email TEXT,
        company_name TEXT,
        has_debt INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Create logs table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        request_body TEXT,
        response_body TEXT
    )
    ''')
    
    # Add some dummy data
    dummy_data = [
        ('Ahmet', 'Yılmaz', '905438851111', 'ahmet@example.com', 'Tech Corp', 0),
        ('Mehmet', 'Demir', '905001112233', 'mehmet@example.com', 'Demir Lojistik', 1)
    ]
    
    try:
        cursor.executemany('''
        INSERT INTO customers (first_name, last_name, phone, email, company_name, has_debt)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', dummy_data)
        print("Database initialized with dummy data.")
    except sqlite3.IntegrityError:
        print("Database already initialized.")
        
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
