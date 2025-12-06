import sqlite3
import os

def fix_db():
    print("Starting database repair...")
    db_path = os.path.join(os.path.dirname(__file__), 'upsc_saga.db')
    conn = sqlite3.connect(db_path)
    
    # 1. Create answer_submissions table
    print("Creating answer_submissions table...")
    conn.execute('''
        CREATE TABLE IF NOT EXISTS answer_submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            question_id INTEGER,
            answer_text TEXT,
            evaluation_json TEXT,
            score REAL,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 2. Create badges tables
    print("Creating badges tables...")
    conn.execute('''
        CREATE TABLE IF NOT EXISTS badges (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            icon TEXT,
            category TEXT,
            rarity TEXT,
            unlock_criteria TEXT,
            xp_reward INTEGER DEFAULT 100
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS user_badges (
            user_id INTEGER,
            badge_id TEXT,
            unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, badge_id),
            FOREIGN KEY (badge_id) REFERENCES badges (id)
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS badge_progress (
            user_id INTEGER,
            badge_id TEXT,
            current_value INTEGER DEFAULT 0,
            target_value INTEGER,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, badge_id)
        )
    ''')

    # 3. Create custom_bosses table
    print("Creating custom_bosses table...")
    conn.execute('''
        CREATE TABLE IF NOT EXISTS custom_bosses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            filters TEXT NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 4. Create test_results VIEW
    print("Creating test_results view...")
    conn.execute('DROP VIEW IF EXISTS test_results')
    conn.execute('''
        CREATE VIEW test_results AS 
        SELECT * FROM test_attempts
    ''')

    # 5. Fix Pomodoro Duration
    print("Fixing pomodoro_sessions duration...")
    try:
        conn.execute('ALTER TABLE pomodoro_sessions ADD COLUMN duration INTEGER')
        conn.execute('UPDATE pomodoro_sessions SET duration = duration_minutes WHERE duration IS NULL')
    except:
        pass

    conn.commit()
    conn.close()
    print("✅ Database repair completed!")

if __name__ == "__main__":
    fix_db()
