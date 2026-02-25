# backend/app/db_models/calendar.py
from app.db import get_db

def init_calendar_tables():
    """Initialize Calendar Event Metadata table"""
    conn = get_db()

    conn.execute('''
        CREATE TABLE IF NOT EXISTS calendar_event_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER DEFAULT 1,
            event_id TEXT UNIQUE NOT NULL, -- Google Calendar ID
            subject TEXT,
            topic TEXT,
            is_completed BOOLEAN DEFAULT 0,
            completion_notes TEXT,
            xp_awarded INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
