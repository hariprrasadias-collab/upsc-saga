import requests
import json
import datetime

BASE_URL = "http://localhost:5000/api/planner"

def test_generate():
    print("Testing Generate Plan (Persistence Check)...")
    today = datetime.date.today().isoformat()
    try:
        # First Call
        res = requests.post(f"{BASE_URL}/generate", json={"start_date": today})
        print(f"First Call: {res.json()}")
        
        # Second Call (Should return existing)
        res = requests.post(f"{BASE_URL}/generate", json={"start_date": today})
        print(f"Second Call: {res.json()}")
        
        # Force New
        res = requests.post(f"{BASE_URL}/generate", json={"start_date": today, "force_new": True})
        print(f"Force New: {res.json()}")
        
    except Exception as e:
        print(f"Failed: {e}")

def test_get_current():
    print("\nTesting Get Current Plan (Smart Slots)...")
    today = datetime.date.today().isoformat()
    try:
        res = requests.get(f"{BASE_URL}/current?start_date={today}&days=7")
        data = res.json()
        if data.get('success'):
            print(f"Plan retrieved. Days: {len(data['plan'])}")
            # Check for weekend slots
            for day in data['plan']:
                if "Saturday" in day['day'] or "Sunday" in day['day']:
                    print(f"Weekend Found ({day['day']}): {len(day['slots'])} slots")
                    if day['slots']:
                        print(f"Sample Activity: {day['slots'][0]['activity']}")
        else:
            print("Failed to get plan")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    test_generate()
    test_get_current()
