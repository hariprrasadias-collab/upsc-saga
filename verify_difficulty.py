import requests
import json
import sqlite3
from datetime import datetime

BASE_URL = "http://localhost:5000/api"
DB_PATH = "backend/upsc_saga.db"

def setup_mock_performance():
    print("Setting up mock performance...")
    conn = sqlite3.connect(DB_PATH)
    
    # Insert High Performance Topic
    conn.execute("DELETE FROM weak_area_analysis WHERE topic = 'MasteredTopic'")
    conn.execute('''
        INSERT INTO weak_area_analysis
        (user_id, topic, subject, total_attempts, correct_attempts, 
         accuracy_rate, priority_score, trend, last_attempt_date, updated_at)
        VALUES (1, 'MasteredTopic', 'MasteredSubject', 20, 20, 100.0, 0.0, 'improving', ?, ?)
    ''', (datetime.now().isoformat(), datetime.now().isoformat()))
    
    # Clear existing opportunities
    conn.execute("DELETE FROM brain_optimization_opportunities WHERE payload LIKE '%MasteredTopic%'")
    
    conn.commit()
    conn.close()
    print("Mock performance inserted.")

def verify_difficulty_adjustment():
    print("Triggering optimization scan...")
    try:
        resp = requests.get(f"{BASE_URL}/autonomy/optimizations")
        data = resp.json()
        
        print(f"Opportunities Found: {data.get('count')}")
        
        found = False
        for opp in data.get('opportunities', []):
            print(f"- [{opp['type']}] {opp['description']}")
            if opp['type'] == 'difficulty_adjustment':
                found = True
                print(f"✅ SUCCESS: Found difficulty adjustment: {opp['description']}")
                break
        
        if not found:
            print("❌ FAILURE: Did not find difficulty adjustment.")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    setup_mock_performance()
    verify_difficulty_adjustment()
