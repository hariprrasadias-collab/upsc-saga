import sqlite3
import os

# Define DB path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'upsc_saga.db')

def migrate():
    print(f"Connecting to database at {DATABASE}...")
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Check if column exists
    cursor.execute("PRAGMA table_info(tasks)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'priority' not in columns:
        print("Adding 'priority' column to 'tasks' table...")
        try:
            cursor.execute("ALTER TABLE tasks ADD COLUMN priority TEXT DEFAULT 'medium'")
            conn.commit()
            print("Migration successful: 'priority' column added.")
        except Exception as e:
            print(f"Error adding column: {e}")
    else:
        print("'priority' column already exists.")
        
    conn.close()

if __name__ == '__main__':
    migrate()
