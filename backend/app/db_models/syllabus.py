from app.db import get_db

def init_syllabus_tables():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS syllabus_topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            paper TEXT, -- GS1, GS2, etc.
            topic TEXT NOT NULL,
            sub_topic TEXT,
            status TEXT DEFAULT 'Not Started',
            notes TEXT,
            importance TEXT DEFAULT 'Medium',
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Topic Revisions Table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS topic_revisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic_id INTEGER NOT NULL,
            revision_count INTEGER DEFAULT 0,
            last_revised_at TIMESTAMP,
            next_revision_date DATE,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (topic_id) REFERENCES syllabus_topics (id)
        )
    ''')

    # Ensure columns exist for legacy schemas
    try:
        conn.execute('ALTER TABLE syllabus_topics ADD COLUMN paper TEXT')
    except:
        pass

    conn.commit()
