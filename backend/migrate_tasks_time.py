import sqlite3
import os

db_path = os.path.join(os.getcwd(), 'upsc_saga.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE tasks ADD COLUMN start_time TEXT")
    print("Added start_time column")
except Exception as e:
    print(f"start_time column might already exist: {e}")

try:
    cursor.execute("ALTER TABLE tasks ADD COLUMN end_time TEXT")
    print("Added end_time column")
except Exception as e:
    print(f"end_time column might already exist: {e}")

conn.commit()
conn.close()
