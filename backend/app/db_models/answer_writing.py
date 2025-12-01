from app.db import get_db

def init_answer_writing_tables():
    """Initialize tables for Answer Writing module"""
    conn = get_db()
    
    # Prompts table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS answer_writing_prompts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            subject TEXT NOT NULL,
            topic TEXT,
            difficulty TEXT DEFAULT 'Medium',
            word_limit INTEGER DEFAULT 250,
            model_answer TEXT,
            keywords TEXT, -- JSON array
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # User Answers table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS user_answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            prompt_id INTEGER NOT NULL,
            answer_text TEXT NOT NULL,
            word_count INTEGER,
            time_taken INTEGER, -- seconds
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (prompt_id) REFERENCES answer_writing_prompts (id)
        )
    ''')
    
    # Evaluations table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS answer_evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            answer_id INTEGER NOT NULL,
            overall_score REAL,
            structure_score REAL,
            content_score REAL,
            relevance_score REAL,
            keyword_coverage REAL,
            strengths TEXT, -- JSON array
            improvements TEXT, -- JSON array
            missing_keywords TEXT, -- JSON array
            evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (answer_id) REFERENCES user_answers (id)
        )
    ''')
    
    conn.commit()
