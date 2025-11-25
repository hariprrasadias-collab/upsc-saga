import sqlite3
import os
from datetime import datetime, timedelta

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'upsc_saga.db')

def migrate():
    print(f"Migrating database at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create challenges table (templates for daily challenges)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS challenges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            type TEXT NOT NULL,
            target_value INTEGER NOT NULL,
            xp_reward INTEGER DEFAULT 50,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create user_challenges table (assigned challenges per user per day)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_challenges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            challenge_id INTEGER NOT NULL,
            assigned_date DATE NOT NULL,
            completed BOOLEAN DEFAULT 0,
            completed_at TIMESTAMP,
            progress INTEGER DEFAULT 0,
            FOREIGN KEY (challenge_id) REFERENCES challenges(id),
            UNIQUE(user_id, assigned_date)
        )
    ''')
    
    # Create streaks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS streaks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            current_streak INTEGER DEFAULT 0,
            longest_streak INTEGER DEFAULT 0,
            last_activity_date DATE,
            streak_freezes INTEGER DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    print("Created challenge tables.")
    
    # Seed challenge templates
    challenge_templates = [
        # Quick Quiz Challenges
        ("Quick Quiz Burst", "Answer 5 multiple choice questions correctly", "mcq", 5, 50),
        ("Quiz Marathon", "Answer 10 multiple choice questions correctly", "mcq", 10, 100),
        
        # Study Time Challenges
        ("Morning Study Session", "Study for 30 minutes before 10 AM", "study_time", 30, 75),
        ("Focused Sprint", "Complete a 45-minute focused study session", "study_time", 45, 100),
        ("Study Marathon", "Study for 2 hours today", "study_time", 120, 200),
        
        # Flashcard Challenges
        ("Flashcard Review", "Review 10 flashcards", "flashcards", 10, 50),
        ("Master Reviewer", "Review 25 flashcards", "flashcards", 25, 100),
        
       # Writing Challenges
        ("Daily Writer", "Write one answer (150 words minimum)", "answer_writing", 1, 75),
        ("Essay Practice", "Write one complete essay", "essay", 1, 150),
        
        # Task Completion Challenges
        ("Task Warrior", "Complete 3 tasks from your War Map", "tasks", 3, 60),
        ("Productivity King", "Complete 5 tasks today", "tasks", 5, 100),
        
        # Current Affairs Challenges
        ("News Reader", "Read 3 current affairs articles", "ravens", 3, 50),
        ("Current Affairs Master", "Read 5 articles and make notes", "ravens", 5, 100),
        
        # Mock Test Challenges
        ("Mini Mock", "Complete a 10-question practice test", "mock_test", 10, 100),
        ("Mock Master", "Score above 70% in a mock test", "mock_test_score", 70, 150),
        
        # CSAT Challenges
        ("Quant Quick", "Solve 5 CSAT quantitative questions", "csat_quant", 5, 50),
        ("Reasoning Rush", "Solve 5 CSAT reasoning questions", "csat_reasoning", 5, 50),
        
        # Syllabus Challenges
        ("Topic Explorer", "Mark 3 syllabus topics as completed", "syllabus", 3, 75),
        
        # Consistency Challenges
        ("Early Bird", "Complete any activity before 6 AM", "early_bird", 1, 100),
        ("Night Owl Scholar", "Study after 10 PM", "night_owl", 1, 75),
    ]
    
    cursor.executemany('''
        INSERT INTO challenges (title, description, type, target_value, xp_reward)
        VALUES (?, ?, ?, ?, ?)
    ''', challenge_templates)
    
    print(f"Seeded {len(challenge_templates)} challenge templates.")
    
    # Initialize streak for user 1
    cursor.execute('''
        INSERT OR IGNORE INTO streaks (user_id, current_streak, longest_streak)
        VALUES (1, 0, 0)
    ''')
    
    print("Initialized streak tracking.")
    
    conn.commit()
    conn.close()
    print("Migration complete!")

if __name__ == '__main__':
    migrate()
