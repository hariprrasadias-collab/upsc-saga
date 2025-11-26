import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'upsc_saga.db')

def migrate():
    print("Creating model_answers table...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create model_answers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS model_answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER,
            title TEXT NOT NULL,
            question_text TEXT NOT NULL,
            answer_text TEXT NOT NULL,
            word_count INTEGER,
            score INTEGER,
            year INTEGER,
            paper TEXT,
            tags TEXT,
            question_type TEXT,
            source TEXT DEFAULT 'custom',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (question_id) REFERENCES pyq_questions(id)
        )
    ''')
    
    # Create indexes for fast search
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_model_answers_paper 
        ON model_answers(paper)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_model_answers_type 
        ON model_answers(question_type)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_model_answers_year 
        ON model_answers(year)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_model_answers_score 
        ON model_answers(score)
    ''')
    
    conn.commit()
    conn.close()
    
    print("✅ model_answers table created successfully!")
    print("✅ Indexes created for fast search")

if __name__ == '__main__':
    migrate()
