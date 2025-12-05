from app.db import get_db

def init_revision_tables():
    conn = get_db()

    conn.execute('''
        CREATE TABLE IF NOT EXISTS revision_cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic_id INTEGER,
            title TEXT NOT NULL,
            one_liner TEXT,
            full_content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS mnemonics_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mnemonic_text TEXT NOT NULL,
            original_text TEXT,
            mnemonic_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
