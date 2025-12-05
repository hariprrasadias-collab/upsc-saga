import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'upsc_saga.db')

def check_syllabus_count():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    try:
        count = conn.execute('SELECT COUNT(*) as c FROM syllabus_topics').fetchone()['c']
        print(f"Syllabus Topics Count: {count}")
        
        if count > 0:
            sample = conn.execute('SELECT * FROM syllabus_topics LIMIT 1').fetchone()
            print(f"Sample Topic: {dict(sample)}")
    except Exception as e:
        print(f"Error: {e}")
        
    conn.close()

if __name__ == "__main__":
    check_syllabus_count()
