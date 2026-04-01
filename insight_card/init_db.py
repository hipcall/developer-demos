import sqlite3
import os

DB_PATH = './data/insight_card.db'
os.makedirs('./data', exist_ok=True)

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

c.execute('DROP TABLE IF EXISTS contacts')
c.execute('DROP TABLE IF EXISTS card_logs')

c.execute('''
    CREATE TABLE IF NOT EXISTS contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phone_number TEXT UNIQUE NOT NULL,
        full_name TEXT NOT NULL,
        company TEXT NOT NULL,
        balance TEXT DEFAULT '0.00'
    )
''')

c.execute('''
    CREATE TABLE IF NOT EXISTS card_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        call_id TEXT NOT NULL,
        caller_number TEXT,
        contact_name TEXT,
        contact_company TEXT,
        status TEXT,
        response_code INTEGER,
        raw_payload TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

dummy = [
    ('902121234567', 'Ahmet Yilmaz', 'Bulutfon Telekom', '150.50'),
    ('905321234567', 'Ayse Demir', 'Acme Yazilim', '42.00'),
    ('905551234567', 'Mehmet Kaya', 'Demo Teknoloji', '0.00'),
    ('905060508169', 'Tarık Akkoyunlu', 'Bulutfon', '1250.00'),
]

for phone, name, company, balance in dummy:
    c.execute('INSERT OR IGNORE INTO contacts (phone_number, full_name, company, balance) VALUES (?,?,?,?)',
              (phone, name, company, balance))

conn.commit()
conn.close()
print(f"Database ready at {DB_PATH}")
