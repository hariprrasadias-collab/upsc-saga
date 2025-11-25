import sqlite3
import os

# Database path - should match the one in db.py (backend/upsc_saga.db)
DB_PATH = os.path.join(os.path.dirname(__file__), 'upsc_saga.db')

def migrate():
    print(f"Migrating database at {DB_PATH}...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create mimir_chat_history table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS mimir_chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        role TEXT NOT NULL, -- 'user' or 'model'
        content TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    print("Created mimir_chat_history table.")
    
    conn.commit()
    conn.close()
    print("Migration complete!")

if __name__ == '__main__':
    migrate()
