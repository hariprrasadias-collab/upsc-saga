import sys
import os
import sqlite3
import json
from unittest.mock import MagicMock

# Add backend directory to path
sys.path.append(os.path.abspath('d:/upsc-second-brain/backend'))

from flask import Flask, g
from app.routes.scribe import scribe_bp
from app.services.mimir_service import mimir_service

app = Flask(__name__)
app.config['DATABASE'] = 'd:/upsc-second-brain/backend/upsc_saga.db'
app.register_blueprint(scribe_bp)

def get_db_connection():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
    return db

def test_scribe_evaluation():
    print("Testing Scribe Evaluation...")
    
    # Mock Mimir Service to return a markdown-formatted JSON string
    mock_response = """
    Here is the evaluation:
    ```json
    {
        "score": 8.5,
        "strengths": ["Good structure", "Clear points"],
        "weaknesses": ["None"],
        "improvements": ["Keep it up"],
        "model_comparison": "Close to ideal"
    }
    ```
    """
    mimir_service.evaluate_answer = MagicMock(return_value=mock_response)
    
    with app.test_client() as client:
        # Mock get_db in the app context
        # We can't easily mock get_db inside the route without patching app.db
        # But since we are using the real DB file, we just need to make sure the table exists (which we did)
        
        response = client.post('/api/scribe/evaluate', json={
            'question': 'Test Question',
            'answer': 'Test Answer'
        })
        
        if response.status_code == 200:
            data = response.get_json()
            print("SUCCESS: Evaluation successful!")
            print(f"ID: {data['id']}")
            print(f"Score: {data['score']}")
            print(f"Feedback: {data['feedback']}")
        else:
            print(f"FAILED: Status {response.status_code}")
            print(response.get_json())

def test_scribe_history():
    print("\nTesting Scribe History...")
    with app.test_client() as client:
        response = client.get('/api/scribe/history')
        
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
    test_scribe_evaluation()
    test_scribe_history()
