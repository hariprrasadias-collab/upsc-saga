import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'upsc_saga.db')

def migrate():
    print(f"Migrating database at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create topic_revisions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS topic_revisions (
        topic_id INTEGER PRIMARY KEY,
        last_revised_at TIMESTAMP,
        revision_count INTEGER DEFAULT 0,
        next_revision_date DATE,
        status TEXT DEFAULT 'pending',
        FOREIGN KEY (topic_id) REFERENCES syllabus_topics (id)
    )
    ''')
    
    print("Created topic_revisions table.")
    
    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == '__main__':
    migrate()
