import requests
import json
import sqlite3
from datetime import datetime

BASE_URL = "http://localhost:5000/api"
DB_PATH = "d:/upsc-second-brain/backend/upsc_saga.db"

def setup_mock_weakness():
    print("Setting up mock weakness...")
    conn = sqlite3.connect(DB_PATH)
    
    # Clear existing weak areas for clean test
    conn.execute("DELETE FROM weak_area_analysis WHERE topic = 'MockWeakness'")
    
    # Insert a mock weak area
    conn.execute('''
        INSERT INTO weak_area_analysis
        (user_id, topic, subject, total_attempts, correct_attempts, 
         accuracy_rate, priority_score, trend, last_attempt_date, updated_at)
        VALUES (1, 'MockWeakness', 'MockSubject', 10, 2, 20.0, 80.0, 'declining', ?, ?)
    ''', (datetime.now().isoformat(), datetime.now().isoformat()))
    
    # Clear existing opportunities for this topic
    conn.execute("DELETE FROM brain_optimization_opportunities WHERE payload LIKE '%MockWeakness%'")
    
    conn.commit()
    conn.close()
    print("Mock weakness inserted.")

def verify_scheduling_opportunity():
    print("Triggering optimization scan...")
    try:
        resp = requests.get(f"{BASE_URL}/autonomy/optimizations")
        data = resp.json()
        
        print(f"Opportunities Found: {data.get('count')}")
        
        found = False
        for opp in data.get('opportunities', []):
            print(f"- [{opp['type']}] {opp['description']}")
            if opp['type'] == 'study_schedule' and 'MockWeakness' in opp['description']:
                found = True
                print("✅ SUCCESS: Found scheduling opportunity for MockWeakness!")
                break
        
        if not found:
            print("❌ FAILURE: Did not find scheduling opportunity.")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    setup_mock_weakness()
    verify_scheduling_opportunity()
