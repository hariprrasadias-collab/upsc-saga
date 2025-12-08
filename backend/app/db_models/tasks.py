from app.db import get_db

def init_tasks_table():
    """Initialize the tasks table (legacy/core tasks)"""
    conn = get_db()

    conn.execute('''
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
