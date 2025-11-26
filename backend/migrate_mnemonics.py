import sqlite3
import os

DB_PATH = 'upsc_saga.db'

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"Database {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        print("Migrating database: Adding mnemonics_history table...")
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mnemonics_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER DEFAULT 1,
                mnemonic_text TEXT NOT NULL,
                original_text TEXT NOT NULL,
                mnemonic_type TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        print("Migration successful: mnemonics_history table created.")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
