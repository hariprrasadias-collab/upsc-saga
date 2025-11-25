import sqlite3
import os

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'upsc_saga.db')

def migrate():
    print(f"Migrating database at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'hacksilver' not in columns:
            print("Adding hacksilver column to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN hacksilver INTEGER DEFAULT 0")
            print("Column added.")
        else:
            print("hacksilver column already exists.")
            
    except Exception as e:
        print(f"Error: {e}")
    
    conn.commit()
    conn.close()
    print("Migration complete!")

if __name__ == '__main__':
    migrate()
