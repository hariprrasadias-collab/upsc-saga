import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'upsc_saga.db')

def check_plan():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    print("--- Checking Active Plan ---")
    plan = conn.execute('SELECT * FROM study_plans WHERE is_active = 1').fetchone()
    if not plan:
        print("No active plan found!")
        return
        
    print(f"Active Plan ID: {plan['id']}")
    print(f"Range: {plan['start_date']} to {plan['end_date']}")
    
    print("\n--- Checking Tasks (Sample) ---")
    tasks = conn.execute('SELECT * FROM study_tasks WHERE plan_id = ? LIMIT 5', (plan['id'],)).fetchall()
    for t in tasks:
        print(f"[{t['date']} {t['start_time']}-{t['end_time']}] {t['subject']}: {t['topic']}")
        
    count = conn.execute('SELECT COUNT(*) FROM study_tasks WHERE plan_id = ?', (plan['id'],)).fetchone()[0]
    print(f"\nTotal Tasks Imported: {count}")
    
    conn.close()

if __name__ == "__main__":
    check_plan()
