import requests
import json
import datetime

BASE_URL = "http://localhost:5000/api/planner"

def test_update_status():
    print("\n--- Testing Update Status ---")
    # 1. Get current plan to find a task
    today = datetime.date.today().isoformat()
    res = requests.get(f"{BASE_URL}/current?start_date={today}&days=1")
    data = res.json()
    
    if not data['success'] or not data['plan']:
        print("FAIL: No plan found to test status update.")
        return

    # Pick first task
    first_day = data['plan'][0]
    if not first_day['slots']:
        print("FAIL: No slots found today.")
        return
        
    task = first_day['slots'][0]
    task_id = task['id']
    print(f"Testing Task ID: {task_id} ({task['subject']})")
    
    # 2. Mark Complete
    print("Marking Complete...")
    res = requests.put(f"{BASE_URL}/task/{task_id}/status", json={"status": "completed"})
    print(f"Response: {res.status_code} - {res.json()}")
    
    # Verify
    res = requests.get(f"{BASE_URL}/current?start_date={today}&days=1")
    updated_task = res.json()['plan'][0]['slots'][0]
    if updated_task['status'] == 'completed':
        print("SUCCESS: Task marked completed.")
    else:
        print(f"FAIL: Task status is {updated_task['status']}")

    # 3. Mark Pending (Revert)
    print("Marking Pending...")
    res = requests.put(f"{BASE_URL}/task/{task_id}/status", json={"status": "pending"})
    
    # Verify
    res = requests.get(f"{BASE_URL}/current?start_date={today}&days=1")
    updated_task = res.json()['plan'][0]['slots'][0]
    if updated_task['status'] == 'pending':
        print("SUCCESS: Task reverted to pending.")
    else:
        print(f"FAIL: Task status is {updated_task['status']}")

def test_yearly_fetch():
    print("\n--- Testing Yearly Fetch (365 days) ---")
    today = datetime.date.today().isoformat()
    res = requests.get(f"{BASE_URL}/current?start_date={today}&days=365")
    data = res.json()
    
    if data['success']:
        days_count = len(data['plan'])
        print(f"SUCCESS: Fetched {days_count} days.")
        if days_count >= 365:
            print("SUCCESS: Full year data retrieved.")
        else:
            print("WARNING: Less than 365 days retrieved (Plan might be shorter).")
    else:
        print(f"FAIL: Fetch failed - {data}")

if __name__ == "__main__":
    try:
        test_update_status()
        test_yearly_fetch()
    except Exception as e:
        print(f"ERROR: {e}")
