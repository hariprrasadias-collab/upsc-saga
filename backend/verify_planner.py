import requests
import json

def test_planner():
    try:
        res = requests.post('http://localhost:5000/api/planner/generate', json={'start_date': '2025-01-01'})
        if res.status_code == 200:
            data = res.json()
            if data['success']:
                print("✅ Plan Generated Successfully")
                print(f"Total Days: {len(data['plan'])}")
                print("First Day Slots:")
                for slot in data['plan'][0]['slots']:
                    print(f"  - {slot['time']}: {slot.get('activity')} ({slot.get('subject', 'Free')})")
            else:
                print("❌ Failed:", data.get('error'))
                print("Trace:", data.get('trace'))
        else:
            print(f"❌ HTTP Error: {res.status_code}")
            try:
                print(res.json())
            except:
                print(res.text)
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    test_planner()
