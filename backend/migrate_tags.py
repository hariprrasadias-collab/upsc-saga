import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'upsc_saga.db')

def migrate():
    print(f"Migrating database at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if tags column exists
        cursor.execute("PRAGMA table_info(current_affairs)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'tags' not in columns:
            print("Adding 'tags' column to current_affairs table...")
            cursor.execute("ALTER TABLE current_affairs ADD COLUMN tags TEXT")
            print("Column added successfully.")
        else:
            print("'tags' column already exists.")
            
        conn.commit()
        print("Migration complete.")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
