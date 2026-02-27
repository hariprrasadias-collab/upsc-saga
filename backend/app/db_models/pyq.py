from app.db import get_db

def init_pyq_tables():
    """Initialize Previous Year Questions module tables"""
    conn = get_db()

    # PYQ Questions Table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS pyq_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER,
            subject TEXT,
            topic TEXT,
            question_text TEXT,
            option_a TEXT,
            option_b TEXT,
            option_c TEXT,
            option_d TEXT,
            correct_option TEXT,
            explanation TEXT,
            difficulty TEXT,
            is_favorite BOOLEAN DEFAULT 0
        )
    ''')

    # Quiz Sessions Table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS pyq_quiz_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER DEFAULT 1,
            title TEXT,
            total_questions INTEGER,
            filters TEXT, -- JSON
            score REAL,
            correct_count INTEGER,
            incorrect_count INTEGER,
            duration_seconds INTEGER,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            submitted_at TIMESTAMP,
            status TEXT DEFAULT 'in_progress'
        )
    ''')

    # Quiz Answers Table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS pyq_quiz_answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            question_id INTEGER,
            selected_answer TEXT,
            is_correct BOOLEAN,
            time_spent INTEGER,
            marked_for_review BOOLEAN DEFAULT 0,
            FOREIGN KEY (session_id) REFERENCES pyq_quiz_sessions (id),
            FOREIGN KEY (question_id) REFERENCES pyq_questions (id)
        )
    ''')

    conn.commit()
