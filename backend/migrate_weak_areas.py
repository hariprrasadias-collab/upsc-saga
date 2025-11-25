# Weak Area Analysis Migration
import sqlite3
from datetime import datetime

def migrate():
    conn = sqlite3.connect('upsc_saga.db')
    cursor = conn.cursor()
    
    # Create weak_area_analysis table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weak_area_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            topic TEXT NOT NULL,
            subject TEXT NOT NULL,
            total_attempts INTEGER DEFAULT 0,
            correct_attempts INTEGER DEFAULT 0,
            accuracy_rate REAL DEFAULT 0.0,
            last_attempt_date TEXT,
            trend TEXT DEFAULT 'stable',
            priority_score REAL DEFAULT 0.0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Create targeted_practice_sets table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS targeted_practice_sets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            set_name TEXT NOT NULL,
            focus_topics TEXT NOT NULL,
            question_ids TEXT NOT NULL,
            total_questions INTEGER DEFAULT 0,
            completed INTEGER DEFAULT 0,
            score REAL DEFAULT 0.0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            completed_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Create practice_set_results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS practice_set_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            practice_set_id INTEGER NOT NULL,
            question_id INTEGER NOT NULL,
            is_correct INTEGER DEFAULT 0,
            time_taken INTEGER DEFAULT 0,
            attempted_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (practice_set_id) REFERENCES targeted_practice_sets(id)
        )
    ''')
    
    # Create index for faster queries
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_weak_area_user_topic 
        ON weak_area_analysis(user_id, topic)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_practice_sets_user 
        ON targeted_practice_sets(user_id, completed)
    ''')
    
    conn.commit()
    print("✅ Weak Area Analysis tables created successfully!")
    
    # Analyze existing data to populate weak_area_analysis
    print("📊 Analyzing existing performance data...")
    
    # Get mock test performance by topic
    cursor.execute('''
        SELECT 
            att.user_id,
            q.subject,
            q.topic,
            COUNT(*) as total_attempts,
            SUM(CASE WHEN ans.is_correct = 1 THEN 1 ELSE 0 END) as correct_attempts
        FROM test_answers ans
        JOIN test_questions q ON ans.question_id = q.id
        JOIN test_attempts att ON ans.attempt_id = att.id
        WHERE att.user_id IS NOT NULL
        GROUP BY att.user_id, q.subject, q.topic
        HAVING total_attempts >= 1
    ''')
    
    mock_results = cursor.fetchall()
    
    for result in mock_results:
        user_id, subject, topic, total, correct = result
        accuracy = (correct / total * 100) if total > 0 else 0
        
        # Calculate priority score (lower accuracy = higher priority)
        priority = (100 - accuracy) * (total / 10)  # Weight by attempts
        
        # Determine trend (simplified for initial data)
        trend = 'declining' if accuracy < 50 else 'stable'
        
        cursor.execute('''
            INSERT OR REPLACE INTO weak_area_analysis 
            (user_id, topic, subject, total_attempts, correct_attempts, accuracy_rate, priority_score, trend)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, topic, subject, total, correct, accuracy, priority, trend))
    
    print(f"✅ Analyzed {len(mock_results)} topic performance records")
    
    conn.commit()
    conn.close()
    print("🎉 Migration complete!")

if __name__ == '__main__':
    migrate()
