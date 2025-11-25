import sqlite3
import os

DB_PATH = 'd:/upsc-second-brain/backend/upsc_saga.db'

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Creating scribe_evaluations table...")
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scribe_evaluations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                question_text TEXT NOT NULL,
                answer_text TEXT NOT NULL,
                score REAL,
                feedback_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("Table created successfully.")
        conn.commit()
    except Exception as e:
        print(f"Error creating table: {e}")
            
    conn.close()

if __name__ == "__main__":
    migrate()
