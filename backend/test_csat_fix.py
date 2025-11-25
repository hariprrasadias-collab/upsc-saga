import sys
import os
import sqlite3
import json

# Add backend directory to path
sys.path.append(os.path.abspath('d:/upsc-second-brain/backend'))

from flask import Flask, g
from app.routes.csat import csat_bp

app = Flask(__name__)
app.config['DATABASE'] = 'd:/upsc-second-brain/backend/upsc_saga.db'
app.register_blueprint(csat_bp)

def get_db_connection():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
    return db

def test_csat_topics():
    print("Testing CSAT Topics...")
    with app.test_client() as client:
        # Mock get_db in the app context
        # We rely on the real DB file existing
        
        response = client.get('/api/csat/topics')
        
        if response.status_code == 200:
            data = response.get_json()
            print("SUCCESS: Topics fetched!")
            print(f"Categories found: {list(data.keys())}")
            for cat, topics in data.items():
                print(f"  - {cat}: {len(topics)} topics")
        else:
            print(f"FAILED: Status {response.status_code}")
            print(response.get_json())

def test_csat_questions():
    print("\nTesting CSAT Questions...")
    with app.test_client() as client:
        # Test fetching questions for a specific category and topic
        category = "Quant"
        topic = "Time & Work"
        
        response = client.get(f'/api/csat/questions?category={category}&topic={topic}')
        
        if response.status_code == 200:
            data = response.get_json()
            print(f"SUCCESS: Questions fetched for {category} - {topic}!")
            print(f"Count: {len(data)}")
            if len(data) > 0:
                print(f"Sample Question: {data[0]['question_text'][:50]}...")
                print(f"Options: {data[0]['options']}")
        else:
            print(f"FAILED: Status {response.status_code}")
            print(response.get_json())

if __name__ == "__main__":
    # Ensure we are in the backend directory for relative imports if needed
    os.chdir('d:/upsc-second-brain/backend')
    test_csat_topics()
    test_csat_questions()
