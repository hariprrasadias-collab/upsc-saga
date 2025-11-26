import sqlite3
import os

DB_PATH = os.path.join('backend', 'upsc_saga.db')

def check_csat():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='csat_questions'")
    table = cursor.fetchone()
    
    if not table:
        print("Table 'csat_questions' does NOT exist.")
    else:
        print("Table 'csat_questions' exists.")
        # Count rows
        cursor.execute("SELECT COUNT(*) FROM csat_questions")
        count = cursor.fetchone()[0]
        print(f"Row count: {count}")
        
        if count > 0:
            cursor.execute("SELECT DISTINCT category FROM csat_questions")
            categories = cursor.fetchall()
            print(f"Categories: {categories}")

    conn.close()

if __name__ == "__main__":
    check_csat()
