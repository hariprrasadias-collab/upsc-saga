from app.db import get_db

def init_gamification_tables():
    """Initialize tables for Gamification (Challenges, Streaks, Rewards)"""
    conn = get_db()
    
    # 1. Challenges Table (The catalog of available challenges)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS challenges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            type TEXT NOT NULL, -- 'daily', 'weekly', 'milestone'
            target_metric TEXT, -- 'hours_studied', 'questions_solved', 'flashcards_reviewed'
            target_value INTEGER DEFAULT 1,
            xp_reward INTEGER DEFAULT 50,
            hacksilver_reward INTEGER DEFAULT 10,
            icon TEXT,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    # 2. User Challenges (Assignments and Progress)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS user_challenges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER DEFAULT 1,
            challenge_id INTEGER,
            assigned_date TEXT NOT NULL, -- YYYY-MM-DD
            progress INTEGER DEFAULT 0,
            completed BOOLEAN DEFAULT 0,
            completed_at TIMESTAMP,
            FOREIGN KEY (challenge_id) REFERENCES challenges (id)
        )
    ''')
    
    # 3. Streaks (Daily Activity Tracking)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS streaks (
            user_id INTEGER PRIMARY KEY,
            current_streak INTEGER DEFAULT 0,
            longest_streak INTEGER DEFAULT 0,
            last_activity_date TEXT -- YYYY-MM-DD
        )
    ''')
    
    # 4. Seed Initial Challenges (if empty)
    existing = conn.execute('SELECT count(*) FROM challenges').fetchone()[0]
    if existing == 0:
        challenges = [
            ('Daily Focus', 'Study for 4 hours today', 'daily', 'hours_studied', 4, 100, 20, 'clock'),
            ('Flashcard Master', 'Review 50 flashcards', 'daily', 'flashcards_reviewed', 50, 50, 10, 'card'),
            ('Answer Writer', 'Write 2 answers today', 'daily', 'answers_written', 2, 150, 30, 'pen'),
            ('Mock Warrior', 'Complete 1 mock test', 'daily', 'mock_tests', 1, 200, 50, 'sword'),
            ('Early Bird', 'Start studying before 6 AM', 'daily', 'start_time', 6, 50, 10, 'sun')
        ]
        conn.executemany('''
            INSERT INTO challenges (title, description, type, target_metric, target_value, xp_reward, hacksilver_reward, icon)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', challenges)
        print("🌱 Seeded initial challenges.")
        
    conn.commit()
