import sqlite3
import os

# Correct Path based on app/db.py: os.path.join(BASE_DIR, 'upsc_saga.db')
# BASE_DIR is parent of app/db.py, which is backend/app/.. -> backend/
DB_PATH = os.path.join(os.getcwd(), 'upsc_saga.db')

def patch_db():
    target_db_path = DB_PATH
    if not os.path.exists(target_db_path):
        print(f"❌ Database not found at {target_db_path}")
        # Fallback check
        alt_path = os.path.join(os.getcwd(), 'instance', 'upsc_saga.sqlite')
        if os.path.exists(alt_path):
             print(f"⚠️ Found DB at instance/upsc_saga.sqlite instead. Patching that.")
             target_db_path = alt_path
        else:
             print("❌ Could not locate any database.")
             return

    conn = sqlite3.connect(target_db_path)
    cursor = conn.cursor()
    
    print(f">> Patching Database at: {target_db_path}")

    # 1. Fix Custom Bosses Table
    try:
        cursor.execute("ALTER TABLE custom_bosses ADD COLUMN name TEXT")
        print(">> Added 'name' column to custom_bosses")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print(">> 'name' column already exists in custom_bosses")
        else:
            print(f"!! Error patching custom_bosses: {e}")

    # 2. Create Syllabus Tracker Table
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS syllabus_tracker (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                topic TEXT NOT NULL,
                sub_topic TEXT,
                status TEXT DEFAULT 'Not Started',
                priority TEXT DEFAULT 'Medium',
                completed_at DATETIME
            )
        ''')
        print(">> Verified/Created 'syllabus_tracker' table")
    except Exception as e:
        print(f"!! Error creating syllabus_tracker: {e}")

    conn.commit()
    conn.close()
    print(">> Database Patch Complete")

if __name__ == "__main__":
    patch_db()
