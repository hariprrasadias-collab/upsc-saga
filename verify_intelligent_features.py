import sys
import os
import datetime
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app import create_app
from app.services.study_planner import generate_study_plan, get_tasks_for_date
from app.db import get_db

app = create_app()

with app.app_context():
    start_date = "2025-11-27"
    print(f"--- Generating Plan for {start_date} ---")
    result = generate_study_plan(start_date, force_new=True)
    
    if not result['success']:
        print("FAIL: Plan generation failed")
        sys.exit(1)
        
    print(f"Plan ID: {result['plan_id']}")
    
    # 1. Verify Sunday Schedule (Full Schedule)
    # Find first Sunday
    d = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    days_to_sunday = (6 - d.weekday()) % 7
    if days_to_sunday == 0: days_to_sunday = 7
    first_sunday = d + datetime.timedelta(days=days_to_sunday)
    
    print(f"\n--- Verifying Sunday ({first_sunday}) ---")
    tasks = get_tasks_for_date(first_sunday.isoformat())
    
    mock_found = False
    analysis_found = False
    flashcard_found = False
    buffer_found = False
    
    for t in tasks:
        print(f"[{t['start_time']}-{t['end_time']}] {t['subject']}: {t['topic']}")
        if "Mock Test" in t['subject']: mock_found = True
        if "Analysis" in t['subject']: analysis_found = True
        if "Flashcards" in t['subject']: flashcard_found = True
        if "Buffer" in t['subject']: buffer_found = True
        
    if mock_found and analysis_found and flashcard_found:
        print("SUCCESS: Sunday has Full Schedule (Mock, Analysis, Flashcards)")
    else:
        print("FAIL: Sunday is missing components!")
        
    # 2. Verify Flashcard Triggers (Smart Flashcards)
    print(f"\n--- Verifying Flashcard Triggers (Scanning 60 days) ---")
    flashcard_count = 0
    chapter_count = 0
    
    for i in range(60):
        check_date = d + datetime.timedelta(days=i)
        tasks = get_tasks_for_date(check_date.isoformat())
        for t in tasks:
            if t['subject'] in ['History', 'Geography', 'Polity', 'Economy', 'Science', 'Environment']:
                chapter_count += 1
            if "Flashcards" in t['subject'] and "Active Recall" in t['topic']:
                flashcard_count += 1
                print(f"Found Triggered Flashcard on {check_date}: {t['topic']}")
                
    print(f"Total Chapters: {chapter_count}")
    print(f"Total Flashcard Sessions: {flashcard_count}")
    
    if flashcard_count > 0:
        print("SUCCESS: Smart Flashcards are being generated.")
    else:
        print("FAIL: No Smart Flashcards found (Check trigger logic).")

    # 3. Verify Dynamic Mocks
    print(f"\n--- Verifying Dynamic Mocks ---")
    # Check a later Sunday
    later_sunday = first_sunday + datetime.timedelta(days=14)
    tasks = get_tasks_for_date(later_sunday.isoformat())
    for t in tasks:
        if "Mock Test" in t['subject']:
            print(f"Mock on {later_sunday}: {t['topic']}")
            if "Recent Chapters" in t['topic']:
                print("SUCCESS: Dynamic Mock Topic verified.")
            else:
                print("WARNING: Mock topic might be generic.")
