import requests
import json
import sqlite3

BASE_URL = "http://localhost:5000/api"
DB_PATH = "d:/upsc-second-brain/backend/upsc_saga.db"

def verify_goal_suggestion():
    print("Verifying Goal Suggestion...")
    conn = sqlite3.connect(DB_PATH)
    
    # Ensure no goals exist
    conn.execute("DELETE FROM brain_goals")
    conn.execute("DELETE FROM brain_optimization_opportunities WHERE type = 'goal_setting'")
    conn.commit()
    conn.close()
    
    try:
        resp = requests.get(f"{BASE_URL}/autonomy/optimizations")
        data = resp.json()
        
        found = False
        for opp in data.get('opportunities', []):
            if opp['type'] == 'goal_setting':
                found = True
                print(f"✅ SUCCESS: Found goal suggestion: {opp['description']}")
                break
        
        if not found:
            print("❌ FAILURE: Did not find goal suggestion.")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    verify_goal_suggestion()
