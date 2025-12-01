# Manual initialization script

if __name__ == "__main__":
    # We need to be in app context or just use get_db if it works directly
    # But get_db uses flask.g
    # So we might need to manually connect
    
    import sqlite3
    DB_PATH = "d:/upsc-second-brain/backend/upsc_saga.db"
    
    # We can just copy the SQL or try to use the function if we can mock flask.g
    # Easier to just run the SQL directly here for speed
    
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS brain_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL DEFAULT 1,
            title TEXT NOT NULL,
            type TEXT NOT NULL, -- 'syllabus', 'questions', 'hours', 'accuracy'
            target_value REAL NOT NULL,
            current_value REAL DEFAULT 0,
            deadline TIMESTAMP,
            status TEXT DEFAULT 'active', -- 'active', 'completed', 'failed'
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    print("✅ brain_goals table created manually.")
