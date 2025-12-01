import os
import sys
import csv
import datetime
from flask import Flask
from dotenv import load_dotenv

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db import get_db
from app.db_models.study_plan import create_new_plan, add_tasks_bulk

# Load environment variables
load_dotenv()

app = Flask(__name__)

CSV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend/public/UPSC_Scheduler.csv'))

def parse_csv_and_sync():
    print(f"Reading CSV from: {CSV_PATH}")
    
    tasks_buffer = []
    
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader) # Skip header
        
        # Date,Day,Slot Type,Time,Subject,Topic,Activity Type,Resources
        
        for row in reader:
            if len(row) < 6:
                continue
                
            date_str = row[0].strip()
            time_range = row[3].strip() # e.g., "04:00 - 05:00"
            subject = row[4].strip()
            topic = row[5].strip()
            activity_type = row[6].strip()
            resources = row[7].strip() if len(row) > 7 else ""
            
            # Parse Time
            try:
                start_time, end_time = time_range.split('-')
                start_time = start_time.strip()
                end_time = end_time.strip()
            except:
                start_time = "00:00"
                end_time = "00:00"
                
            # Create Task Tuple
            # (plan_id, date, start_time, end_time, subject, topic, resource_link, status)
            # We'll set plan_id later
            tasks_buffer.append({
                "date": date_str,
                "start": start_time,
                "end": end_time,
                "subject": subject,
                "topic": f"{topic} ({activity_type})",
                "link": resources
            })
            
    print(f"Parsed {len(tasks_buffer)} tasks from CSV.")
    
    with app.app_context():
        # 1. Create New Plan
        start_date = tasks_buffer[0]['date']
        end_date = tasks_buffer[-1]['date']
        print(f"Creating new plan from {start_date} to {end_date}...")
        
        plan_id = create_new_plan(start_date, end_date)
        print(f"Created Plan ID: {plan_id}")
        
        # 2. Insert Tasks
        db_tasks = []
        for t in tasks_buffer:
            db_tasks.append((
                plan_id, 
                t['date'], 
                t['start'], 
                t['end'], 
                t['subject'], 
                t['topic'], 
                t['link'], 
                'pending'
            ))
            
        print("Inserting tasks into database...")
        add_tasks_bulk(db_tasks)
        print("Sync Complete!")

if __name__ == "__main__":
    parse_csv_and_sync()
