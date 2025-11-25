import sqlite3
import os

# Database path
db_path = os.path.join(os.path.dirname(__file__), 'upsc_saga.db')

def migrate_pyq_quiz():
    print(f"Connecting to database at {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create PYQ Quiz Sessions Table
    print("Creating pyq_quiz_sessions table...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pyq_quiz_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER DEFAULT 1,
            title TEXT NOT NULL,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            submitted_at TIMESTAMP,
            duration_seconds INTEGER,
            score REAL,
            total_questions INTEGER NOT NULL,
            correct_count INTEGER DEFAULT 0,
            incorrect_count INTEGER DEFAULT 0,
            filters TEXT,
            status TEXT DEFAULT 'in_progress',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create PYQ Quiz Answers Table
    print("Creating pyq_quiz_answers table...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pyq_quiz_answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            question_id INTEGER NOT NULL,
            selected_answer TEXT,
            is_correct BOOLEAN,
            time_spent INTEGER DEFAULT 0,
            marked_for_review BOOLEAN DEFAULT 0,
            FOREIGN KEY (session_id) REFERENCES pyq_quiz_sessions(id),
            FOREIGN KEY (question_id) REFERENCES pyq_questions(id)
        )
    ''')

    conn.commit()
    
    # Check if data exists
    cursor.execute('SELECT count(*) FROM pyq_quiz_sessions')
    count = cursor.fetchone()[0]
    
    if count == 0:
        print("No existing quiz sessions. Ready for use.")
    else:
        print(f"Found {count} existing quiz sessions.")

    conn.close()
    print("PYQ Quiz Migration completed successfully!")

if __name__ == '__main__':
    migrate_pyq_quiz()
