import sqlite3

def create_user_stats_table():
    conn = sqlite3.connect('upsc_saga.db')
    c = conn.cursor()
    
    print("Creating user_stats table...")
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER DEFAULT 1,
            date TEXT NOT NULL,
            study_hours REAL DEFAULT 0,
            tasks_completed INTEGER DEFAULT 0,
            xp_earned INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            current_streak INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert a dummy record to prevent empty table errors
    c.execute('''
        INSERT INTO user_stats (user_id, date, study_hours, tasks_completed, xp_earned, level, current_streak)
        SELECT 1, date('now'), 0, 0, 0, 1, 0
        WHERE NOT EXISTS (SELECT 1 FROM user_stats)
    ''')
    
    conn.commit()
    conn.close()
    print("Table created successfully.")

if __name__ == "__main__":
    create_user_stats_table()
