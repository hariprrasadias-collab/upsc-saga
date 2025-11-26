import sqlite3
import os

DB_PATH = 'backend/upsc_saga.db'

def check_db():
    print(f"Checking database at {DB_PATH}...")
    if not os.path.exists(DB_PATH):
        print("Database file not found!")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # 1. Check Schema
        print("\n--- Schema Check ---")
        cursor.execute("PRAGMA table_info(current_affairs)")
        columns = cursor.fetchall()
        column_names = [col['name'] for col in columns]
        print(f"Columns: {column_names}")
        
        if 'tags' not in column_names:
            print("CRITICAL: 'tags' column missing!")
        else:
            print("'tags' column exists.")

        # 2. Check Data for Article 353 (from user error)
        print("\n--- Data Check (ID: 353) ---")
        cursor.execute("SELECT * FROM current_affairs WHERE id = 353")
        article = cursor.fetchone()
        
        if article:
            print(f"Article found: {article['title']}")
            print(f"Tags value: {article['tags']}")
            
            # Simulate logic
            tags = []
            if article and article['tags']:
                try:
                    tags = article['tags'].split(',')
                    print(f"Parsed tags: {tags}")
                except Exception as e:
                    print(f"Error parsing tags: {e}")
            else:
                print("Tags are empty or None")
        else:
            print("Article 353 not found.")

    except Exception as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_db()
