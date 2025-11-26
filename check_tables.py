import sqlite3

def check_tables():
    try:
        conn = sqlite3.connect('backend/upsc_saga.db')
        cursor = conn.cursor()
        
        # Check columns for pyq_questions
        cursor.execute("PRAGMA table_info(pyq_questions)")
        columns = cursor.fetchall()
        print("\npyq_questions columns:", [c[1] for c in columns])
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_tables()
