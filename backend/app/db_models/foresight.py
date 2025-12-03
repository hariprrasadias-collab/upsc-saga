from app.db import get_db

def init_foresight_tables():
    """Initialize Foresight tables"""
    conn = get_db()
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS foresight_predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER DEFAULT 1,
            question TEXT NOT NULL,
            type TEXT, -- 'MCQ' or 'Essay'
            probability REAL,
            reasoning TEXT,
            subject TEXT,
            topic TEXT,
            preparation_tip TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_favorite BOOLEAN DEFAULT 1
        )
    ''')
    
    conn.commit()
