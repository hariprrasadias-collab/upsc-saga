import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'upsc_saga.db')
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

try:
    rows = cursor.execute("SELECT year, COUNT(*) as count FROM pyq_questions GROUP BY year ORDER BY year DESC").fetchall()
    print("PYQ Questions by Year:")
    for row in rows:
        print(f"{row['year']}: {row['count']}")
        
    total = cursor.execute("SELECT COUNT(*) FROM pyq_questions").fetchone()[0]
    print(f"\nTotal Questions: {total}")
    
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()
