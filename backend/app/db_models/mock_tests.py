from app.db import get_db

def init_mock_test_tables():
    """Initialize tables for Mock Test module"""
    conn = get_db()
    
    # Mock Tests table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS mock_tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            subject TEXT NOT NULL,
            test_type TEXT DEFAULT 'General', -- 'Prelims', 'Mains', 'CSAT'
            difficulty TEXT DEFAULT 'Medium',
            total_questions INTEGER DEFAULT 0,
            duration_minutes INTEGER DEFAULT 120,
            negative_marking REAL DEFAULT 0.33,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Questions table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS test_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            test_id INTEGER NOT NULL,
            question_number INTEGER NOT NULL,
            question_text TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            correct_answer TEXT NOT NULL, -- 'A', 'B', 'C', 'D'
            explanation TEXT,
            subject TEXT,
            topic TEXT,
            marks REAL DEFAULT 2.0,
            FOREIGN KEY (test_id) REFERENCES mock_tests (id)
        )
    ''')
    
    # Attempts table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS test_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            test_id INTEGER NOT NULL,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            submitted_at TIMESTAMP,
            time_taken INTEGER, -- seconds
            total_attempted INTEGER DEFAULT 0,
            total_correct INTEGER DEFAULT 0,
            total_incorrect INTEGER DEFAULT 0,
            total_unattempted INTEGER DEFAULT 0,
            score REAL DEFAULT 0,
            percentage REAL DEFAULT 0,
            status TEXT DEFAULT 'in_progress', -- 'in_progress', 'completed'
            answers TEXT, -- JSON dump of selected answers
            FOREIGN KEY (test_id) REFERENCES mock_tests (id)
        )
    ''')

    # Migration: Add 'answers' column if missing (for existing dbs)
    try:
        cursor = conn.execute("PRAGMA table_info(test_attempts)")
        columns = [row['name'] for row in cursor.fetchall()]
        if 'answers' not in columns:
            print("Migrating: Adding 'answers' column to test_attempts...")
            conn.execute("ALTER TABLE test_attempts ADD COLUMN answers TEXT")
    except Exception as e:
        print(f"Migration warning (test_attempts): {e}")
    
    # User Answers table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS test_answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            attempt_id INTEGER NOT NULL,
            question_id INTEGER NOT NULL,
            selected_answer TEXT, -- 'A', 'B', 'C', 'D'
            is_marked BOOLEAN DEFAULT 0,
            is_correct BOOLEAN,
            FOREIGN KEY (attempt_id) REFERENCES test_attempts (id),
            FOREIGN KEY (question_id) REFERENCES test_questions (id)
        )
    ''')
    
    conn.commit()
