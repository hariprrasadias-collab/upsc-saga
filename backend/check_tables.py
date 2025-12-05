import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'upsc_saga.db')

print(f"Checking database at: {DB_PATH}")

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables found:")
    for table in tables:
        print(f"- {table[0]}")
    conn.close()
except Exception as e:
    print(f"Error: {e}")
