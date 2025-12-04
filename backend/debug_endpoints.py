import requests
import json
import sqlite3
import os

BASE_URL = "http://localhost:5000"

def check_db_count():
    db_path = os.path.join(os.getcwd(), 'upsc_saga.db')
    if not os.path.exists(db_path):
        print(f"!! DB not found at {db_path}")
        return -1
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM tasks WHERE is_quest=1")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def debug_api():
    print(">> Debugging API...")
    
    # 1. Check Initial DB Count (Direct File Access)
    initial_count = check_db_count()
    print(f">> Initial Quest Count in DB (Direct): {initial_count}")

    # 2. Call GENERATE_QUESTS
    url = f"{BASE_URL}/api/brain/execute"
    payload = {"type": "GENERATE_QUESTS", "payload": {}}
    try:
        print(f">> Sending POST to {url}")
        response = requests.post(url, json=payload)
        print(f">> Status Code: {response.status_code}")
        
        try:
            json_resp = response.json()
            print(f">> Response Message: {json_resp.get('message')}")
            if 'debug_info' in json_resp:
                print(f">> SERVER DEBUG INFO: {json.dumps(json_resp['debug_info'], indent=2)}")
            else:
                print("!! No debug_info in response. Server might not be updated.")
        except:
            print(f"!! Failed to parse JSON: {response.text[:100]}")
            
    except Exception as e:
        print(f"!! Request Failed: {e}")

    # 3. Check Final DB Count (Direct File Access)
    final_count = check_db_count()
    print(f">> Final Quest Count in DB (Direct): {final_count}")
    
    # 4. Check API View of Quests
    try:
        print(">> Fetching GET /api/quests...")
        q_res = requests.get(f"{BASE_URL}/api/quests")
        quests = q_res.json()
        print(f">> API Quest Count: {len(quests)}")
        for q in quests:
            print(f"   - [{q['id']}] {q['title']} (Completed: {q['isCompleted']})")
    except Exception as e:
        print(f"!! Failed to fetch quests: {e}")

if __name__ == "__main__":
    debug_api()
