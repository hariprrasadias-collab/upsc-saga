import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'upsc_saga.db')

def migrate():
    """Create tables for performance tracking and weak area detection"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create performance_records table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS performance_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER DEFAULT 1,
            question_id INTEGER NOT NULL,
            topic TEXT,
            subject TEXT,
            is_correct BOOLEAN NOT NULL,
            time_taken INTEGER,
            attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create weak_areas table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weak_areas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL UNIQUE,
            subject TEXT,
            total_attempts INTEGER DEFAULT 0,
            correct_attempts INTEGER DEFAULT 0,
            accuracy_rate REAL DEFAULT 0.0,
            avg_time_taken REAL DEFAULT 0.0,
            weakness_score REAL DEFAULT 0.0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create indexes
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_perf_topic 
        ON performance_records(topic)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_perf_subject 
        ON performance_records(subject)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_weak_score 
        ON weak_areas(weakness_score DESC)
    ''')
    
    conn.commit()
    conn.close()
    
    print("✅ Performance tracking tables created successfully!")
    print("   - performance_records: Track every question attempt")
    print("   - weak_areas: Aggregated weak topic analysis")
    print("   - Indexes on topic, subject, weakness_score")

if __name__ == '__main__':
    migrate()
