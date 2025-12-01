from app.db import get_db

def init_flashcard_tables():
    """Initialize tables for Flashcard module"""
    conn = get_db()
    
    # Decks table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS decks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            subject TEXT DEFAULT 'General',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Flashcards table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS flashcards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            deck_id INTEGER NOT NULL,
            front TEXT NOT NULL,
            back TEXT NOT NULL,
            source TEXT, -- 'manual', 'ai_generated', 'kindle'
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (deck_id) REFERENCES decks (id)
        )
    ''')
    
    # Review Sessions table (Ebisu)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS review_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            flashcard_id INTEGER NOT NULL,
            reviewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            result INTEGER, -- 0=fail, 1=pass
            halflife REAL,
            alpha REAL,
            beta REAL,
            next_review TIMESTAMP,
            FOREIGN KEY (flashcard_id) REFERENCES flashcards (id)
        )
    ''')
    
    conn.commit()
