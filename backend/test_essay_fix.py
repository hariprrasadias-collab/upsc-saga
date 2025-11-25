import sys
import os
import sqlite3
import json
from unittest.mock import MagicMock

# Add backend directory to path
sys.path.append(os.path.abspath('d:/upsc-second-brain/backend'))

from flask import Flask, g
from app.routes.essay import essay_bp, evaluator

app = Flask(__name__)
app.config['DATABASE'] = 'd:/upsc-second-brain/backend/upsc_saga.db'
app.register_blueprint(essay_bp)

def get_db_connection():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
    return db

def test_essay_submission():
    print("Testing Essay Submission...")
    
    # Mock Essay Evaluator
    mock_evaluation = {
        "score": 150,
        "strengths": ["Good flow", "Clear argument"],
        "weaknesses": ["Needs more examples"],
        "suggestions": ["Add case studies"]
    }
    evaluator.evaluate_essay = MagicMock(return_value=mock_evaluation)
    
    with app.test_client() as client:
        # Mock get_db in the app context
        # We rely on the real DB file existing
        
        response = client.post('/api/essay/submit', json={
            'topic': 'Test Essay Topic',
            'content': 'This is a test essay content.'
        })
        
        if response.status_code == 200:
            data = response.get_json()
            print("SUCCESS: Essay submitted!")
            print(f"ID: {data['id']}")
            print(f"Evaluation: {data['evaluation']}")
        else:
            print(f"FAILED: Status {response.status_code}")
            print(response.get_json())

def test_essay_history():
    print("\nTesting Essay History...")
    with app.test_client() as client:
        response = client.get('/api/essay/history')
        
        if response.status_code == 200:
            data = response.get_json()
            print(f"SUCCESS: History fetched! Count: {len(data)}")
            if len(data) > 0:
                print(f"Latest: {data[0]}")
        else:
            print(f"FAILED: Status {response.status_code}")
            print(response.get_json())

if __name__ == "__main__":
    # Ensure we are in the backend directory for relative imports if needed
    os.chdir('d:/upsc-second-brain/backend')
    test_essay_submission()
    test_essay_history()
