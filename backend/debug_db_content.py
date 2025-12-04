import sqlite3
import os

DB_PATH = os.path.join(os.getcwd(), 'upsc_saga.db')

def inspect_db():
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print(f">> Inspecting Database at: {DB_PATH}")

    # 1. Check Syllabus Tracker
    try:
        cursor.execute("SELECT count(*) as count FROM syllabus_tracker")
        count = cursor.fetchone()['count']
        print(f">> Syllabus Tracker Rows: {count}")
        
        if count == 0:
            print("!! Syllabus Tracker is EMPTY. This explains why Prioritize returns 0 results.")
        else:
            cursor.execute("SELECT * FROM syllabus_tracker LIMIT 3")
            rows = cursor.fetchall()
            print(">> Sample Syllabus Items:")
            for r in rows:
                print(dict(r))
    except Exception as e:
        print(f"!! Error checking syllabus_tracker: {e}")

    # 2. Check Quests
    try:
        cursor.execute("SELECT count(*) as count FROM tasks WHERE is_quest=1")
        count = cursor.fetchone()['count']
        print(f">> Total Quests (is_quest=1): {count}")
        
        cursor.execute("SELECT * FROM tasks WHERE is_quest=1 ORDER BY id DESC LIMIT 5")
        rows = cursor.fetchall()
        print(">> Recent Quests:")
        for r in rows:
            print(dict(r))
            
    except Exception as e:
        print(f"!! Error checking quests: {e}")

    conn.close()

if __name__ == "__main__":
    inspect_db()
