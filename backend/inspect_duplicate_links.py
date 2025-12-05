import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'upsc_saga.db')

def inspect_links():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    # Get a set of duplicates
    rows = conn.execute('''
        SELECT original_link, id
        FROM current_affairs 
        WHERE original_link IN (
            SELECT original_link
            FROM current_affairs 
            GROUP BY original_link 
            HAVING COUNT(*) > 1
        )
        ORDER BY original_link
    ''').fetchall()
    
    print(f"Found {len(rows)} duplicate entries.")
    
    for r in rows:
        print(f"ID: {r['id']}")
        print(f"Link Repr: {repr(r['original_link'])}")
        print("-" * 20)
        
    conn.close()

if __name__ == "__main__":
    inspect_links()
