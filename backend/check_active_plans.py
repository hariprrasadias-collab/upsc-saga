import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'upsc_saga.db')

def check_active_plans():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    print("--- Checking Active Plans ---")
    plans = conn.execute('SELECT * FROM study_plans WHERE is_active = 1').fetchall()
    
    print(f"Active Plans Count: {len(plans)}")
    for p in plans:
        print(f"ID: {p['id']} | Start: {p['start_date']} | Created: {p['created_at']}")
        
    conn.close()

if __name__ == "__main__":
    check_active_plans()
