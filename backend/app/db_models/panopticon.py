import sqlite3
import json
from datetime import datetime

def init_panopticon_tables(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Table for Daily Bio-Metrics
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS daily_biometrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT UNIQUE NOT NULL,
        sleep_hours REAL,
        sleep_quality INTEGER, -- 1-10
        mood_score INTEGER, -- 1-10
        energy_level INTEGER, -- 1-10
        diet_quality INTEGER, -- 1-10
        exercise_minutes INTEGER,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Table for Calculated Correlations (Cached analysis)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bio_correlations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        metric_name TEXT, -- e.g., 'sleep_hours'
        performance_metric TEXT, -- e.g., 'quiz_score'
        correlation_coefficient REAL,
        insight_text TEXT,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()
