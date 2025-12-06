from app.db import get_db

def init_syllabus_tables():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS syllabus_topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            topic TEXT NOT NULL,
            sub_topic TEXT,
            status TEXT DEFAULT 'Not Started',
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
