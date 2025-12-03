import sys
import os
import datetime

# Add backend to path
sys.path.append(os.path.abspath('d:/upsc-second-brain/backend'))

from flask import Flask, g
import sqlite3

app = Flask(__name__)
app.config['DATABASE'] = 'd:/upsc-second-brain/backend/upsc_saga.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
    return db

with app.app_context():
    # Mock g._database for the service calls if they use get_db()
    # But study_planner uses app.db_models which imports get_db from app.db
    # We need to make sure app.db.get_db works.
    
    # Let's just import the function and try to run it. 
    # It might fail if it can't find the DB.
    # We might need to patch app.db.get_db
    
    from app.services.study_planner import get_todays_tasks_summary
    
    # We need to ensure the DB connection works within the service
    # The service likely imports 'db' from 'app'. 
    # In a standalone script, 'app' might not be fully initialized.
    
    # Let's try to manually connect and see tasks first.
    conn = sqlite3.connect('d:/upsc-second-brain/backend/upsc_saga.db')
    cursor = conn.cursor()
    today = datetime.date.today().isoformat()
    print(f"Checking tasks for date: {today}")
    
    cursor.execute("SELECT * FROM study_tasks WHERE date = ?", (today,))
    tasks = cursor.fetchall()
    print(f"Found {len(tasks)} tasks in DB (raw SQL).")
    
    # Now try the function
    try:
        from app import db
        # Patch db.get_db to use our connection or a new one
        db.get_db = lambda: sqlite3.connect('d:/upsc-second-brain/backend/upsc_saga.db')
        db.get_db().row_factory = sqlite3.Row
        
        summary = get_todays_tasks_summary()
        print("\n--- SUMMARY OUTPUT ---")
        print(summary)
        print("----------------------")
    except Exception as e:
        print(f"Error running function: {e}")
