import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'upsc_saga.db')

def migrate():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    print("Creating mind_maps table...")
    c.execute('''
        CREATE TABLE IF NOT EXISTS mind_maps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            root_node TEXT NOT NULL, -- JSON string
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Migration completed successfully.")

if __name__ == '__main__':
    migrate()
