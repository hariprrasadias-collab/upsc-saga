import sqlite3
from datetime import datetime, timedelta
import random

def seed_data():
    conn = sqlite3.connect('upsc_saga.db')
    cursor = conn.cursor()
    
    user_id = 1
    
    # 1. Clear existing relevant data
    cursor.execute("DELETE FROM mock_tests")
    cursor.execute("DELETE FROM test_attempts")
    cursor.execute("DELETE FROM syllabus_topics")
    
    # 2. Seed Mock Tests (Subjects)
    subjects = ['History', 'Geography', 'Polity', 'Economy', 'Environment', 'Science & Tech']
    test_ids = {}
    
    print("Seeding Mock Tests...")
    for subj in subjects:
        cursor.execute('''
            INSERT INTO mock_tests (title, description, test_type, subject, total_questions, duration_minutes, total_marks)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (f"{subj} Full Test", f"Comprehensive test for {subj}", "Subject", subj, 100, 120, 200))
        test_ids[subj] = cursor.lastrowid

    # 3. Seed Attempts (Creating trends)
    print("Seeding Attempts...")
    
    # History: Improving (40 -> 80)
    base_date = datetime.now() - timedelta(days=30)
    for i in range(5):
        score = 40 + (i * 10) + random.randint(-5, 5)
        cursor.execute('''
            INSERT INTO test_attempts (user_id, test_id, score, submitted_at, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, test_ids['History'], score, base_date + timedelta(days=i*5), 'completed'))

    # Geography: Declining (70 -> 40)
    for i in range(5):
        score = 70 - (i * 5) + random.randint(-5, 5)
        cursor.execute('''
            INSERT INTO test_attempts (user_id, test_id, score, submitted_at, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, test_ids['Geography'], score, base_date + timedelta(days=i*5), 'completed'))

    # Polity: Stable High (80-90)
    for i in range(5):
        score = 85 + random.randint(-5, 5)
        cursor.execute('''
            INSERT INTO test_attempts (user_id, test_id, score, submitted_at, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, test_ids['Polity'], score, base_date + timedelta(days=i*5), 'completed'))

    # Economy: Low (30-40)
    for i in range(3):
        score = 35 + random.randint(-5, 5)
        cursor.execute('''
            INSERT INTO test_attempts (user_id, test_id, score, submitted_at, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, test_ids['Economy'], score, base_date + timedelta(days=i*5), 'completed'))

    # 4. Seed Syllabus Topics
    print("Seeding Syllabus...")
    topics = [
        ('History', 'Ancient India', 'Not Started'),
        ('History', 'Medieval India', 'Reading'),
        ('Geography', 'Physical Geography', 'Completed'),
        ('Geography', 'Climatology', 'Not Started'),
        ('Polity', 'Constitution', 'Completed'),
        ('Polity', 'Parliament', 'Reading'),
        ('Economy', 'Banking', 'Not Started'),
        ('Environment', 'Biodiversity', 'Not Started'),
    ]
    
    for subj, topic, status in topics:
        cursor.execute('''
            INSERT INTO syllabus_topics (subject, topic, paper, status)
            VALUES (?, ?, ?, ?)
        ''', (subj, topic, 'GS1' if subj in ['History', 'Geography'] else 'GS2' if subj == 'Polity' else 'GS3', status))

    conn.commit()
    conn.close()
    print("Seeding complete!")

if __name__ == "__main__":
    seed_data()
