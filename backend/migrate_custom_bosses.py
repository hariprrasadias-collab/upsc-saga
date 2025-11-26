import sqlite3
import os

# Use absolute path to ensure we hit the right DB
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'upsc_saga.db')

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("Creating Custom Bosses table...")

cursor.execute('''
    CREATE TABLE IF NOT EXISTS custom_bosses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        filters TEXT NOT NULL, -- JSON string of filters
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT 1
    )
''')

conn.commit()
conn.close()

print("✅ Custom Bosses table created successfully!")
