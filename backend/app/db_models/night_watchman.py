"""
Database models for The Night Watchman (Autonomous Research)
"""
from app.db import get_db
import json

def init_watchman_tables():
    """Initialize tables for Night Watchman"""
    conn = get_db()
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS morning_briefings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL, -- YYYY-MM-DD
            summary TEXT, -- The main briefing text (Markdown)
            quote TEXT, -- Motivational quote for the day
            articles_analyzed INTEGER DEFAULT 0,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_read BOOLEAN DEFAULT 0
        )
    ''')
    
    conn.commit()

def save_briefing(briefing_data):
    """Save a generated morning briefing"""
    conn = get_db()
    cursor = conn.execute('''
        INSERT INTO morning_briefings (date, summary, quote, articles_analyzed)
        VALUES (?, ?, ?, ?)
    ''', (
        briefing_data['date'],
        briefing_data['summary'],
        briefing_data.get('quote', ''),
        briefing_data.get('articles_count', 0)
    ))
    conn.commit()
    return cursor.lastrowid

def get_latest_briefing():
    """Get the most recent briefing"""
    conn = get_db()
    row = conn.execute('''
        SELECT * FROM morning_briefings 
        ORDER BY generated_at DESC 
        LIMIT 1
    ''').fetchone()
    
    if row:
        return dict(row)
    return None

def mark_briefing_read(id):
    """Mark a briefing as read"""
    conn = get_db()
    conn.execute('UPDATE morning_briefings SET is_read = 1 WHERE id = ?', (id,))
    conn.commit()
