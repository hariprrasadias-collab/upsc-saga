import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'upsc_saga.db')

def inspect_remaining_schemas():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    tables = ['pyq_questions', 'weak_area_analysis', 'topic_revisions', 'flashcard_reviews']
    
    for table in tables:
        print(f"--- {table} Schema ---")
        try:
            cols = conn.execute(f"PRAGMA table_info({table})").fetchall()
            if not cols:
                print(f"Table {table} does not exist!")
            for c in cols:
                print(f"{c['name']} ({c['type']})")
        except Exception as e:
            print(f"Error checking {table}: {e}")
        print("\n")
        
    conn.close()

if __name__ == "__main__":
    inspect_remaining_schemas()
