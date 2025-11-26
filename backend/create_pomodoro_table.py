import sqlite3

def create_pomodoro_table():
    try:
        conn = sqlite3.connect('upsc_saga.db')
        cursor = conn.cursor()
        
        print("Creating pomodoro_sessions table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pomodoro_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER DEFAULT 1,
                timestamp TEXT,
                duration INTEGER,
                xp_awarded INTEGER
            )
        ''')
        
        print("Table created successfully.")
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_pomodoro_table()
