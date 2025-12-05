import sqlite3
import os
import datetime
import sys

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.study_planner import get_plan_for_range

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'upsc_saga.db')

def check_today():
    today = datetime.date.today().isoformat()
    print(f"Checking for date: {today}")
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    # 1. Check raw DB
    print("\n--- Raw DB Check ---")
    plan = conn.execute('SELECT * FROM study_plans WHERE is_active = 1').fetchone()
    if not plan:
        print("No active plan!")
        return
    
    print(f"Active Plan ID: {plan['id']}")
    
    tasks = conn.execute('''
        SELECT * FROM study_tasks 
        WHERE plan_id = ? AND date = ?
    ''', (plan['id'], today)).fetchall()
    
    print(f"Tasks found in DB for today: {len(tasks)}")
    for t in tasks:
        print(f"  [{t['start_time']}] {t['subject']}")

    # 2. Check Service Function
    print("\n--- Service Function Check (get_plan_for_range) ---")
    try:
        # Simulate what the frontend asks for (usually starts from today or start of week)
        # Let's ask for today
        result = get_plan_for_range(today, days=1)
        print(f"Service returned {len(result)} days")
        if result:
            day_plan = result[0]
            print(f"Date: {day_plan['date']}")
            print(f"Slots: {len(day_plan['slots'])}")
            for s in day_plan['slots']:
                print(f"  {s['time']} - {s['subject']}")
    except Exception as e:
        print(f"Service Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_today()
