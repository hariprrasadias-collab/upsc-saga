import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'upsc_saga.db')

def create_tasks_table():
    print(f"Connecting to database at {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("Creating tasks table if not exists...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            xp_reward INTEGER NOT NULL,
            associated_stat TEXT,
            due_date TEXT NOT NULL,
            isCompleted INTEGER DEFAULT 0,
            is_quest INTEGER DEFAULT 0,
            start_time TEXT,
            end_time TEXT,
            priority TEXT DEFAULT 'medium',
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Tasks table created successfully.")

if __name__ == '__main__':
    create_tasks_table()
