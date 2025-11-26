import sqlite3
import os

db_path = os.path.join('backend', 'upsc_saga.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='badges'")
print(cursor.fetchone()[0])
conn.close()
