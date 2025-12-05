import csv
import sqlite3
import os
import sys
from datetime import datetime

# Add backend directory to path so we can import app modules if needed
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'upsc_saga.db')
CSV_PATH = os.path.join(BASE_DIR, '..', 'frontend', 'public', 'UPSC_Scheduler.csv')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def import_csv():
    print(f"Importing from {CSV_PATH}...")
    
    if not os.path.exists(CSV_PATH):
        print("Error: CSV file not found!")
        return

    conn = get_db()
    
    # 1. Create a new Active Study Plan
    # Determine start and end date from CSV
    dates = []
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Date'] and row['Date'] != 'Date':
                try:
                    # Validate format
                    datetime.strptime(row['Date'], '%Y-%m-%d')
                    dates.append(row['Date'])
                except ValueError:
                    pass
    
    if not dates:
        print("Error: No data found in CSV.")
        return

    dates.sort()
    start_date = dates[0]
    end_date = dates[-1]
    
    print(f"Plan Range: {start_date} to {end_date}")

    # Deactivate old plans
    conn.execute('UPDATE study_plans SET is_active = 0 WHERE is_active = 1')
    
    # Insert new plan
    cursor = conn.execute('''
        INSERT INTO study_plans (start_date, end_date, is_active)
        VALUES (?, ?, 1)
    ''', (start_date, end_date))
    plan_id = cursor.lastrowid
    print(f"Created new Study Plan ID: {plan_id}")

    # 2. Insert Tasks
    tasks_to_insert = []
    
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # CSV Columns: Date,Day,Slot_Type,Time,Subject,Topic,Activity_Type,Resources
            date_str = row['Date']
            time_range = row['Time'] # e.g., "04:00-04:50"
            subject = row['Subject']
            topic = row['Topic']
            activity_type = row['Activity_Type']
            resources = row['Resources']
            
            if not time_range or '-' not in time_range:
                continue
                
            start_time, end_time = time_range.split('-')
            
            # Combine Topic and Activity Type for better description
            full_topic = f"{topic} ({activity_type})"
            
            tasks_to_insert.append((
                plan_id,
                date_str,
                start_time.strip(),
                end_time.strip(),
                subject,
                full_topic,
                resources,
                'pending'
            ))

    print(f"Found {len(tasks_to_insert)} tasks to insert.")
    
    conn.executemany('''
        INSERT INTO study_tasks (
            plan_id, date, start_time, end_time, 
            subject, topic, resource_link, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', tasks_to_insert)
    
    conn.commit()
    conn.close()
    print("Import completed successfully!")

if __name__ == "__main__":
    import_csv()
