import sqlite3
from app.db import get_db

def init_mind_palace_tables():
    conn = get_db()
    cursor = conn.cursor()
    
    # Locations: Virtual spaces (e.g., "Library", "Parliament House")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mind_palace_locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            image_url TEXT, -- Background image for the location
            layout_type TEXT DEFAULT 'grid', -- 'grid', 'freeform', '3d'
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Artifacts: Memory items placed in locations
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mind_palace_artifacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT, -- The fact/concept to remember
            type TEXT DEFAULT 'note', -- 'note', 'image', 'audio', 'flashcard'
            x_position INTEGER DEFAULT 0,
            y_position INTEGER DEFAULT 0,
            z_position INTEGER DEFAULT 0, -- For 3D support
            color TEXT DEFAULT '#ffffff',
            icon TEXT DEFAULT '📝',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (location_id) REFERENCES mind_palace_locations (id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
