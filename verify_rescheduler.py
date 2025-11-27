import requests
import datetime
import sqlite3
import json

BASE_URL = "http://localhost:5000/api/planner"
DB_PATH = "d:/upsc-second-brain/backend/upsc_saga.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def setup_test_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get active plan ID
    plan = cursor.execute("SELECT id FROM study_plans WHERE is_active = 1").fetchone()
    if not plan:
        print("No active plan found. Please generate one first.")
        return None
    plan_id = plan['id']
    
    today = datetime.date.today()
    yesterday = (today - datetime.timedelta(days=1)).isoformat()
    tomorrow = (today + datetime.timedelta(days=1)).isoformat()
    
    print(f"--- Setting up Test Data ---")
    print(f"Today: {today}, Yesterday: {yesterday}, Tomorrow: {tomorrow}")
    
    # 1. Insert a PAST PENDING TASK
    cursor.execute('''
        INSERT INTO study_tasks (plan_id, date, start_time, end_time, subject, topic, status)
        VALUES (?, ?, '10:00', '11:00', 'History', 'TEST_PENDING_TASK', 'pending')
    ''', (plan_id, yesterday))
    pending_task_id = cursor.lastrowid
    print(f"Created Past Pending Task ID: {pending_task_id}")
    
    # 2. Insert a FUTURE BUFFER SLOT
    cursor.execute('''
        INSERT INTO study_tasks (plan_id, date, start_time, end_time, subject, topic, status)
        VALUES (?, ?, '20:00', '21:00', 'Buffer', 'Catch-up / Free Time', 'pending')
    ''', (plan_id, tomorrow))
    buffer_task_id = cursor.lastrowid
    print(f"Created Future Buffer Slot ID: {buffer_task_id}")
    
    conn.commit()
    conn.close()
    return pending_task_id, buffer_task_id, tomorrow

def verify_rescheduling(pending_id, buffer_id, expected_date):
    print("\n--- Triggering Reschedule ---")
    try:
        response = requests.post(f"{BASE_URL}/reschedule-check")
        print(f"API Response: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"API Call Failed: {e}")
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check Pending Task
    task = cursor.execute("SELECT * FROM study_tasks WHERE id = ?", (pending_id,)).fetchone()
    if task:
        print(f"\nTask {pending_id} Status: {task['status']}")
        print(f"Task {pending_id} Date: {task['date']} (Expected: {expected_date})")
        
        if task['date'] == expected_date and task['status'] == 'rescheduled':
            print("SUCCESS: Task was rescheduled correctly.")
        else:
            print("FAILURE: Task was NOT rescheduled correctly.")
    else:
        print("FAILURE: Task not found!")
        
    # Check Buffer Slot
    buffer_slot = cursor.execute("SELECT * FROM study_tasks WHERE id = ?", (buffer_id,)).fetchone()
    if not buffer_slot:
        print(f"SUCCESS: Buffer slot {buffer_id} was consumed (deleted).")
    else:
        print(f"FAILURE: Buffer slot {buffer_id} still exists!")
        
    conn.close()

if __name__ == "__main__":
    data = setup_test_data()
    if data:
        verify_rescheduling(*data)
