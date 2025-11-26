import sqlite3
import os

DB_PATH = 'backend/upsc_saga.db'

def check_schema():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(current_affairs)")
    columns = cursor.fetchall()
    print("Columns:")
    for col in columns:
        print(f"- {col['name']}")
    
    conn.close()

if __name__ == "__main__":
    check_schema()
