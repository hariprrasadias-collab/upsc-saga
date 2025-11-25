import sqlite3
import os

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'app', 'upsc_saga.db')

def migrate():
    print(f"Migrating database at {DB_PATH}...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create essay_submissions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS essay_submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        topic TEXT NOT NULL,
        content TEXT NOT NULL,
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        evaluation_json TEXT,
        score INTEGER,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    print("Created essay_submissions table.")
    
    conn.commit()
    conn.close()
    print("Migration complete!")

if __name__ == '__main__':
    migrate()
