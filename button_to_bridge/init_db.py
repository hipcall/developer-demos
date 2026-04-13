import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'customers.db')

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    ''')
    
    # Insert some dummy records if the table is empty
    cursor.execute('SELECT COUNT(*) FROM customers')
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO customers (name, department, phone) VALUES ('Ahmet Yılmaz', 'Sales', '+905326202911')")
        cursor.execute("INSERT INTO customers (name, department, phone) VALUES ('Ayşe Demir', 'Support', '+905060508169')")
        
    conn.commit()
    conn.close()
    print("Database initialized successfully at", DB_PATH)

if __name__ == '__main__':
    init_db()
