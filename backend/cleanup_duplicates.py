import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'upsc_saga.db')

def cleanup_duplicates():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    print("--- Cleaning up Duplicates ---")
    
    # Find duplicates (same link), keep the one with MAX(id)
    # We want to delete rows that are NOT in the set of MAX(id) per link
    
    cursor = conn.execute('''
        DELETE FROM current_affairs 
        WHERE id NOT IN (
            SELECT MAX(id) 
            FROM current_affairs 
            GROUP BY original_link
        )
    ''')
    
    deleted_count = cursor.rowcount
    conn.commit()
    
    print(f"Deleted {deleted_count} duplicate articles.")
    
    # Verify
    count = conn.execute('''
        SELECT COUNT(*) as c 
        FROM (
            SELECT original_link 
            FROM current_affairs 
            GROUP BY original_link 
            HAVING COUNT(*) > 1
        )
    ''').fetchone()['c']
    
    print(f"Remaining duplicate sets: {count}")
    
    # Create Unique Index to prevent future duplicates
    print("Creating UNIQUE INDEX on original_link...")
    try:
        conn.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_current_affairs_link ON current_affairs(original_link)')
        print("Index created successfully.")
    except Exception as e:
        print(f"Error creating index: {e}")
        
    conn.close()

if __name__ == "__main__":
    cleanup_duplicates()
