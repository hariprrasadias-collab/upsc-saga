import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

import sqlite3
from app.services.syllabus_tracker import SyllabusTracker
from app.db import get_db

# Mock app context
class MockApp:
    def teardown_appcontext(self, f):
        pass

if __name__ == "__main__":
    print("Verifying Syllabus Tracking...")
    
    # We need to manually connect to DB since we are outside Flask app
    # But SyllabusTracker uses get_db() which uses flask.g
    # So we will mock get_db or just modify the service to accept conn?
    # Easier: Just run this inside a minimal flask app context or patch get_db
    
    # Actually, let's just use the same pattern as other verify scripts if possible
    # But wait, other verify scripts used `requests` to hit the API.
    # Here I want to test the service directly.
    
    # Let's create a temporary route in a temp file? No, that's complex.
    # Let's just use raw SQL to verify, and call the service if we can mock flask.g
    
    # Alternative: Create a simple script that imports the service and mocks get_db
    
    import flask
    from unittest.mock import MagicMock
    
    app = flask.Flask(__name__)
    app.config['DATABASE'] = 'd:/upsc-second-brain/backend/upsc_saga.db'
    
    with app.app_context():
        # 1. Reset a topic
        conn = get_db()
        # Pick a topic from migrate_full_syllabus.py
        topic = "World wars"
        conn.execute("UPDATE syllabus_topics SET status = 'Not Started' WHERE topic = ?", (topic,))
        conn.commit()
        
        # 2. Call Service
        print(f"Updating '{topic}' to 'Completed'...")
        result = SyllabusTracker.update_topic_progress(topic, 'Completed')
        print(f"Result: {result}")
        
        # 3. Verify in DB
        row = conn.execute("SELECT status FROM syllabus_topics WHERE topic = ?", (topic,)).fetchone()
        if row and row['status'] == 'Completed':
            print("✅ SUCCESS: Topic status updated.")
        else:
            print(f"❌ FAILURE: Topic status is {row['status'] if row else 'None'}")
            
        # 4. Verify Summary
        summary = SyllabusTracker.get_progress_summary()
        print(f"Progress Summary: {summary}")
