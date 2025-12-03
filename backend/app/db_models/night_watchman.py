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
            mind_map TEXT, -- Mermaid.js syntax
            static_linkage TEXT, -- Book reference
            quiz_data TEXT, -- JSON string of MCQs
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_read BOOLEAN DEFAULT 0
        )
    ''')
    
    # Migration for existing tables (simplistic check)
    try:
        conn.execute('ALTER TABLE morning_briefings ADD COLUMN mind_map TEXT')
    except Exception:
        pass
        
    try:
        conn.execute('ALTER TABLE morning_briefings ADD COLUMN static_linkage TEXT')
    except Exception:
        pass

    try:
        conn.execute('ALTER TABLE morning_briefings ADD COLUMN quiz_data TEXT')
    except Exception:
        pass # Columns likely exist
    
    conn.commit()

def save_briefing(briefing_data):
    """Save a generated morning briefing"""
    conn = get_db()
    
    # Serialize quiz_data if it's a list/dict
    quiz_json = briefing_data.get('quiz', [])
    if isinstance(quiz_json, (list, dict)):
        quiz_json = json.dumps(quiz_json)
        
    cursor = conn.execute('''
        INSERT INTO morning_briefings (date, summary, quote, articles_analyzed, mind_map, static_linkage, quiz_data)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        briefing_data['date'],
        briefing_data['summary'],
        briefing_data.get('quote', ''),
        briefing_data.get('articles_count', 0),
        briefing_data.get('mind_map', ''),
        briefing_data.get('static_linkage', ''),
        quiz_json
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
