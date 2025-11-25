import sys
import os
import sqlite3
import json

# Add backend directory to path
sys.path.append(os.path.abspath('d:/upsc-second-brain/backend'))

from app.services.weak_area_service import weak_area_analyzer
from app.db import get_db
from flask import Flask, g

app = Flask(__name__)
app.config['DATABASE'] = 'd:/upsc-second-brain/backend/upsc_saga.db'

def get_db_connection():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
    return db

def setup_test_data():
    with app.app_context():
        conn = get_db_connection()
        # Ensure we have a weak area to trigger generation
        conn.execute('''
            INSERT OR REPLACE INTO weak_area_analysis 
            (user_id, topic, subject, total_attempts, correct_attempts, accuracy_rate, priority_score, trend, last_attempt_date)
            VALUES (1, 'Ancient History', 'History', 10, 2, 20.0, 80.0, 'declining', '2023-01-01')
        ''')
        
        # Ensure we have questions in questions_master for this topic
        # (Assuming questions_master has data from previous phases, but let's check/insert)
        cursor = conn.execute("SELECT count(*) FROM questions_master WHERE topic = 'Ancient History'")
        count = cursor.fetchone()[0]
        if count == 0:
            print("Inserting dummy question for test...")
            conn.execute('''
                INSERT INTO questions_master (source, subject, topic, difficulty, question_text, options, correct_option, explanation)
                VALUES ('Test', 'History', 'Ancient History', 'Medium', 'Test Question?', '["A", "B"]', 'A', 'Exp')
            ''')
        
        conn.commit()
        print("Test data setup complete.")

def test_generate_practice_set():
    with app.app_context():
        # Mock get_db to return our connection
        # But since we are in app_context, get_db from app.db should work if configured correctly
        # However, app.db uses 'upsc_saga.db' relative path usually.
        # Let's monkeypatch get_db in the service module to be safe or ensure app.db works.
        
        # Actually, let's just use the service as is, but we need to make sure app.db.get_db finds the DB.
        # The app.db module uses `DATABASE = 'upsc_saga.db'`. 
        # We might need to change directory to backend for it to find it, or patch it.
        
        print("Testing generate_practice_set...")
        try:
            # We need to patch get_db in the service because it imports it directly
            # But we can't easily patch it without a library like unittest.mock
            # So let's just run this script from the backend directory so the relative path works.
            
            result = weak_area_analyzer.generate_practice_set(user_id=1, num_questions=5)
            
            if result:
                print("SUCCESS: Practice set generated!")
                print(f"Set ID: {result['practice_set_id']}")
                print(f"Questions: {len(result['questions'])}")
                print(f"Focus: {result['focus_topics']}")
            else:
                print("FAILED: No practice set returned (maybe no weak areas found?)")
                
        except Exception as e:
            print(f"FAILED: Error during generation: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    setup_test_data()
    test_generate_practice_set()
