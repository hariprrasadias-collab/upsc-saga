import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'upsc_saga.db')

def migrate_scribe():
    print(f"Migrating database at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create answer_evaluations table
    print("Creating answer_evaluations table...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS answer_evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            question_id INTEGER,
            question_text TEXT,
            answer_text TEXT NOT NULL,
            score REAL,
            feedback_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()
    print("Scribe Migration complete.")

if __name__ == '__main__':
    migrate_scribe()
