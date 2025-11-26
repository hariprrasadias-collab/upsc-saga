import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'upsc_saga.db')

def migrate():
    """Create issue_mappings table for AI-powered syllabus mapping"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create issue_mappings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS issue_mappings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article_id INTEGER NOT NULL,
            subject TEXT NOT NULL,
            syllabus_topic TEXT NOT NULL,
            paper TEXT,
            relevance_score REAL DEFAULT 0.0,
            key_linkages TEXT,
            exam_utility TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (article_id) REFERENCES current_affairs(id)
        )
    ''')
    
    # Create indexes for efficient queries
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_mappings_article 
        ON issue_mappings(article_id)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_mappings_topic 
        ON issue_mappings(syllabus_topic)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_mappings_subject 
        ON issue_mappings(subject)
    ''')
    
    conn.commit()
    conn.close()
    
    print("✅ issue_mappings table created successfully!")
    print("   - id, article_id, subject, syllabus_topic, paper")
    print("   - relevance_score, key_linkages, exam_utility")
    print("   - Indexes on article_id, syllabus_topic, subject")

if __name__ == '__main__':
    migrate()
