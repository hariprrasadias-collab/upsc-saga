import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'upsc_saga.db')

def check_duplicates():
    conn = sqlite3.connect(DB_PATH)
    
    print("--- Checking for Duplicates ---")
    # Check for tasks with same plan_id, date, start_time
    duplicates = conn.execute('''
        SELECT plan_id, date, start_time, COUNT(*) as c
        FROM study_tasks
        GROUP BY plan_id, date, start_time
        HAVING c > 1
        ORDER BY c DESC
        LIMIT 20
    ''').fetchall()
    
    if duplicates:
        print(f"Found {len(duplicates)} slots with duplicates (showing top 20):")
        for d in duplicates:
            print(f"Plan {d[0]} | {d[1]} {d[2]} : {d[3]} copies")
            
        total_dupes = conn.execute('''
            SELECT SUM(c) - COUNT(*) 
            FROM (
                SELECT COUNT(*) as c
                FROM study_tasks
                GROUP BY plan_id, date, start_time
                HAVING c > 1
            )
        ''').fetchone()[0]
        print(f"\nEstimated total redundant rows: {total_dupes}")
    else:
        print("No duplicates found.")
        
    conn.close()

if __name__ == "__main__":
    check_duplicates()
