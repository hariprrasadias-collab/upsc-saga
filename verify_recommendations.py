import requests
import json
import sqlite3
from datetime import datetime

BASE_URL = "http://localhost:5000/api"
DB_PATH = "backend/upsc_saga.db"

def setup_mock_data():
    print("Setting up mock data...")
    conn = sqlite3.connect(DB_PATH)
    
    # 1. Insert Mock Weakness
    conn.execute("DELETE FROM weak_area_analysis WHERE topic = 'MockTopic'")
    conn.execute('''
        INSERT INTO weak_area_analysis
        (user_id, topic, subject, total_attempts, correct_attempts, 
         accuracy_rate, priority_score, trend, last_attempt_date, updated_at)
        VALUES (1, 'MockTopic', 'MockSubject', 10, 2, 20.0, 90.0, 'declining', ?, ?)
    ''', (datetime.now().isoformat(), datetime.now().isoformat()))
    
    # 2. Insert Mock Article
    conn.execute("DELETE FROM current_affairs WHERE title = 'Mock Article for MockTopic'")
    conn.execute('''
        INSERT INTO current_affairs (title, original_link, source, published_date, upsc_summary)
        VALUES (?, ?, ?, ?, ?)
    ''', ('Mock Article for MockTopic', 'http://mock.com/article', 'MockSource', datetime.now().isoformat(), 'Summary'))
    
    # 3. Clear existing opportunities
    conn.execute("DELETE FROM brain_optimization_opportunities WHERE payload LIKE '%MockTopic%'")
    
    conn.commit()
    conn.close()
    print("Mock data inserted.")

def verify_recommendation():
    print("Triggering optimization scan...")
    try:
        resp = requests.get(f"{BASE_URL}/autonomy/optimizations")
        print(f"Response Status: {resp.status_code}")
        print(f"Response Body: {resp.text}")
        
        data = resp.json()
        
        print(f"Opportunities Found: {data.get('count')}")
        
        found = False
        for opp in data.get('opportunities', []):
            print(f"- [{opp['type']}] {opp['description']}")
            if opp['type'] == 'content_recommendation' and 'MockTopic' in opp['description']:
                found = True
                print("✅ SUCCESS: Found content recommendation for MockTopic!")
                break
        
        if not found:
            print("❌ FAILURE: Did not find content recommendation.")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    setup_mock_data()
    verify_recommendation()
