import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'upsc_saga.db')

def check_duplicates():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    print("--- Checking for Duplicates ---")
    
    # Check for exact link duplicates
    rows = conn.execute('''
        SELECT original_link as link, COUNT(*) as c, GROUP_CONCAT(id) as ids, GROUP_CONCAT(title) as titles 
        FROM current_affairs 
        GROUP BY original_link 
        HAVING c > 1
    ''').fetchall()
    
    if rows:
        print(f"Found {len(rows)} sets of exact link duplicates:")
        for r in rows:
            print(f"Link: {r['link']}")
            print(f"Count: {r['c']}")
            print(f"IDs: {r['ids']}")
            print(f"Titles: {r['titles']}")
            print("-" * 20)
    else:
        print("No exact link duplicates found.")

    # Check for title duplicates (potential slight URL variations)
    print("\n--- Checking for Title Duplicates ---")
    rows = conn.execute('''
        SELECT title, COUNT(*) as c, GROUP_CONCAT(id) as ids, GROUP_CONCAT(original_link) as links
        FROM current_affairs 
        GROUP BY title 
        HAVING c > 1
    ''').fetchall()
    
    if rows:
        print(f"Found {len(rows)} sets of title duplicates:")
        for r in rows:
            print(f"Title: {r['title']}")
            print(f"Count: {r['c']}")
            print(f"IDs: {r['ids']}")
            print(f"Links: {r['links']}")
            print("-" * 20)
    else:
        print("No title duplicates found.")
        
    conn.close()

if __name__ == "__main__":
    check_duplicates()
