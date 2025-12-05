import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'upsc_saga.db')

def inspect_revision_schema():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    print("--- Revision Cards Schema ---")
    cols = conn.execute("PRAGMA table_info(revision_cards)").fetchall()
    for c in cols:
        print(f"{c['name']} ({c['type']})")
        
    conn.close()

if __name__ == "__main__":
    inspect_revision_schema()
