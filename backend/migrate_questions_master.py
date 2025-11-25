import sqlite3
import json

def migrate():
    conn = sqlite3.connect('upsc_saga.db')
    c = conn.cursor()
    
    print("Creating questions_master table...")
    c.execute('''
        CREATE TABLE IF NOT EXISTS questions_master (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL, -- e.g., 'PYQ-2023', 'Mock-Test-1'
            subject TEXT NOT NULL,
            topic TEXT,
            difficulty TEXT DEFAULT 'Medium',
            question_text TEXT NOT NULL,
            options TEXT NOT NULL, -- JSON string of options array
            correct_option TEXT NOT NULL,
            explanation TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create index for faster searching
    c.execute('CREATE INDEX IF NOT EXISTS idx_questions_subject ON questions_master(subject)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_questions_source ON questions_master(source)')
    
    conn.commit()
    conn.close()
    print("Migration complete: questions_master table created.")

if __name__ == "__main__":
    migrate()
