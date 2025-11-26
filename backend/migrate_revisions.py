import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'upsc_saga.db')

def migrate():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    print("Creating revision_schedules table...")
    c.execute('''
        CREATE TABLE IF NOT EXISTS revision_schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_type TEXT NOT NULL, -- 'note', 'article', 'question', 'flashcard'
            item_id INTEGER NOT NULL,
            last_reviewed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            next_review TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            interval INTEGER DEFAULT 0, -- Days until next review
            ease_factor REAL DEFAULT 2.5,
            review_count INTEGER DEFAULT 0,
            UNIQUE(item_type, item_id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Migration completed successfully.")

if __name__ == '__main__':
    migrate()
