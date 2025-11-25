import sqlite3

DB_PATH = 'd:/upsc-second-brain/backend/upsc_saga.db'

def check_schema():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(questions_master)")
    columns = cursor.fetchall()
    
    print("Columns in questions_master:")
    for col in columns:
        print(f"- {col[1]} ({col[2]})")
            
    conn.close()

if __name__ == "__main__":
    check_schema()
