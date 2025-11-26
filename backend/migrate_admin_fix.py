import sqlite3
from app.db import get_db

def migrate():
    conn = sqlite3.connect('backend/upsc_saga.db')
    cursor = conn.cursor()
    
    print("Creating mock_questions table...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mock_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_text TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            correct_option TEXT NOT NULL,
            explanation TEXT,
            subject TEXT NOT NULL,
            topic TEXT NOT NULL,
            difficulty TEXT DEFAULT 'medium',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate()
