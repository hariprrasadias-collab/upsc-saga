import sqlite3
import os
from datetime import datetime

# Database path - should match the one in db.py
DB_PATH = os.path.join(os.path.dirname(__file__), 'upsc_saga.db')

def migrate():
    print(f"Migrating database at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create badges table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS badges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            rarity TEXT NOT NULL,
            icon_url TEXT,
            unlock_criteria TEXT NOT NULL,
            xp_reward INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create user_badges table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_badges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            badge_id INTEGER NOT NULL,
            unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (badge_id) REFERENCES badges(id)
        )
    ''')
    
    # Create badge_progress table  
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS badge_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            badge_id INTEGER NOT NULL,
            current_value INTEGER DEFAULT 0,
            target_value INTEGER NOT NULL,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (badge_id) REFERENCES badges(id),
            UNIQUE(user_id, badge_id)
        )
    ''')
    
    print("Created badge tables.")
    
    # Seed badge definitions
    badges = [
        # Milestone Badges
        ("First Steps", "Complete your first task", "milestone", "common", "🎯", "tasks_completed:1", 50),
        ("Task Master", "Complete 100 tasks", "milestone", "rare", "✅", "tasks_completed:100", 500),
        ("Study Warrior", "Maintain a 7-day streak", "milestone", "rare", "🔥", "streak_days:7", 300),
        ("Inferno", "Maintain a 30-day streak", "milestone", "epic", "🌋", "streak_days:30", 1000),
        ("Centurion", "Reach Level 10", "milestone", "rare", "⭐", "level:10", 500),
        ("Legend", "Reach Level 50", "milestone", "legendary", "👑", "level:50", 5000),
        
        # Mastery Badges
        ("History Buff", "Complete all History topics", "mastery", "rare", "📚", "subject_complete:history", 800),
        ("Geography Expert", "Complete all Geography topics", "mastery", "rare", "🌍", "subject_complete:geography", 800),
        ("Polity Pro", "Complete all Polity topics", "mastery", "rare", "⚖️", "subject_complete:polity", 800),
        ("Economy Ace", "Complete all Economy topics", "mastery", "rare", "💰", "subject_complete:economy", 800),
        ("Perfect Score", "Score 100% in a mock test", "mastery", "epic", "💯", "mock_test_perfect:1", 1500),
        ("Quiz Champion", "Answer 1000 questions correctly", "mastery", "epic", "🎓", "correct_answers:1000", 2000),
        
        # Practice Badges
        ("Wordsmith", "Write 50 answers", "practice", "common", "✍️", "answers_written:50", 400),
        ("Essay Expert", "Write 20 essays", "practice", "rare", "📝", "essays_written:20", 600),
        ("Flashcard Fanatic", "Review 500 flashcards", "practice", "rare", "🎴", "flashcards_reviewed:500", 500),
        ("Mock Master", "Complete 10 mock tests", "practice", "rare", "📋", "mock_tests:10", 700),
        
        # Social Badges (Future)
        ("Helping Hand", "Help 10 fellow aspirants", "social", "rare", "🤝", "helps_given:10", 500),
        
        # Special Badges
        ("Early Bird", "Complete a task before 6 AM", "special", "rare", "🌅", "early_task:1", 300),
        ("Night Owl", "Complete a task after 11 PM", "special", "rare", "🦉", "late_task:1", 300),
        ("Speed Demon", "Complete 10 tasks in one day", "special", "epic", "⚡", "daily_tasks:10", 1000),
        ("Comeback Kid", "Return after 7 days of inactivity", "special", "rare", "🔄", "return_after_break:1", 400),
        
        # XP Milestones
        ("XP Hunter", "Earn 1000 total XP", "milestone", "common", "🎯", "total_xp:1000", 200),
        ("XP Warrior", "Earn 10000 total XP", "milestone", "rare", "⚔️", "total_xp:10000", 1000),
        ("XP Legend", "Earn 50000 total XP", "milestone", "epic", "🏆", "total_xp:50000", 5000),
        
        # CSAT Badges
        ("Math Whiz", "Complete 100 CSAT quant questions", "practice", "rare", "🧮", "csat_quant:100", 600),
        ("Logic Master", "Complete 100 CSAT reasoning questions", "practice", "rare", "🧠", "csat_reasoning:100", 600),
    ]
    
    # Insert badges
    cursor.executemany('''
        INSERT INTO badges (name, description, category, rarity, icon_url, unlock_criteria, xp_reward)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', badges)
    
    print(f"Seeded {len(badges)} badges.")
    
    conn.commit()
    conn.close()
    print("Migration complete!")

if __name__ == '__main__':
    migrate()
