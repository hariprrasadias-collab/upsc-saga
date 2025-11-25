import sqlite3
import os

DB_PATH = 'd:/upsc-second-brain/backend/upsc_saga.db'

def check_tables():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    tables = ['weak_area_analysis', 'targeted_practice_sets', 'practice_set_results', 'mock_questions', 'test_questions', 'questions_master']
    
    print("Checking tables...")
    for table in tables:
        try:
            cursor.execute(f"SELECT count(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"[OK] Table '{table}' exists. Rows: {count}")
        except sqlite3.OperationalError as e:
            print(f"[MISSING] Table '{table}' does not exist. Error: {e}")
            
    conn.close()

if __name__ == "__main__":
    check_tables()
