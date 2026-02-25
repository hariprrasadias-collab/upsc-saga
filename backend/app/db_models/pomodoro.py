from app.db import get_db

def init_pomodoro_tables():
    """Initialize Pomodoro module tables"""
    conn = get_db()

    # Pomodoro Sessions Table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS pomodoro_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER DEFAULT 1,
            task_id INTEGER,
            duration INTEGER, -- seconds (used by analytics)
            duration_minutes INTEGER, -- legacy/backup
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            focus_score INTEGER,
            notes TEXT,
            xp_awarded INTEGER DEFAULT 0
        )
    ''')

    conn.commit()
