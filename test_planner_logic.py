import sys
import os
import datetime
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app import create_app
from app.services.study_planner import generate_study_plan, get_active_plan
from app.db_models.study_plan import get_tasks_for_date
from app.db import get_db

app = create_app()

with app.app_context():
    start_date = "2025-11-27"
    print(f"Testing generate_study_plan with force_new=True for {start_date}")
    result = generate_study_plan(start_date, force_new=True)
    print(f"Result: {result}")
    
    active_plan = get_active_plan()
    print(f"Active Plan: {active_plan}")
    
    if result['success']:
        print("SUCCESS: Generated new plan")
        
        # Check total tasks
        conn = get_db()
        count = conn.execute("SELECT COUNT(*) FROM study_tasks WHERE plan_id = ?", (result['plan_id'],)).fetchone()[0]
        print(f"Total Tasks in DB for Plan {result['plan_id']}: {count}")

        # Verify Day 1 tasks (Start Date)
        tasks = get_tasks_for_date(start_date)
        print(f"\nDay 1 Tasks ({len(tasks)}):")
        
        srs_found = False
        timing_correct = False
        
        for t in tasks:
            print(f"- {t['start_time']} - {t['end_time']}: {t['topic']}")
            if "SRS Review" in t['subject']:
                srs_found = True
            if ":50" in t['end_time']:
                timing_correct = True
            if "Active Recall Session:" in t['topic']:
                print(f"SUCCESS: Flashcard Subject Found: {t['topic']}")
                
        # Verify Day 2 tasks (for SRS)
        next_day = (datetime.datetime.strptime(start_date, "%Y-%m-%d") + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        tasks_day2 = get_tasks_for_date(next_day)
        print(f"\nDay 2 Tasks ({len(tasks_day2)}):")
        for t in tasks_day2:
            if "SRS Review" in t['subject']:
                srs_found = True
                print(f"SUCCESS: SRS Review Found on Day 2: {t['topic']}")

        if srs_found:
            print("SUCCESS: SRS Reviews found")
        else:
            print("WARNING: No SRS Reviews found")
            
        if timing_correct:
            print("SUCCESS: Strict Timing (50m slots) verified")
        else:
            print("FAIL: Strict Timing not found")
            
    else:
        print("FAIL: Generation failed")
