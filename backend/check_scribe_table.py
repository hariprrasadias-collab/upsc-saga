import sqlite3
import os

DB_PATH = 'd:/upsc-second-brain/backend/upsc_saga.db'

def check_table():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT count(*) FROM answer_evaluations")
        count = cursor.fetchone()[0]
        print(f"[OK] Table 'answer_evaluations' exists. Rows: {count}")
        
        # Check columns
        cursor.execute("PRAGMA table_info(answer_evaluations)")
        columns = cursor.fetchall()
        print("Columns:")
        for col in columns:
            print(f"- {col[1]} ({col[2]})")
            
    except sqlite3.OperationalError as e:
        print(f"[MISSING] Table 'answer_evaluations' does not exist. Error: {e}")
            
    conn.close()

if __name__ == "__main__":
    check_table()
