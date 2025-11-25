import sqlite3

def create_missing_tables():
    conn = sqlite3.connect('upsc_saga.db')
    c = conn.cursor()
    
    print("Creating mock_test_results table...")
    c.execute('''
        CREATE TABLE IF NOT EXISTS mock_test_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER DEFAULT 1,
            test_id INTEGER,
            score REAL,
            total_marks REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    print("Creating flashcard_reviews table...")
    c.execute('''
        CREATE TABLE IF NOT EXISTS flashcard_reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER DEFAULT 1,
            flashcard_id INTEGER,
            rating INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    print("Creating battle_history table...")
    c.execute('''
        CREATE TABLE IF NOT EXISTS battle_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER DEFAULT 1,
            boss_id INTEGER,
            outcome TEXT,
            damage_dealt REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert dummy data to prevent empty table errors
    print("Inserting dummy data...")
    c.execute("INSERT INTO mock_test_results (score, total_marks) SELECT 0, 200 WHERE NOT EXISTS (SELECT 1 FROM mock_test_results)")
    c.execute("INSERT INTO flashcard_reviews (flashcard_id, rating) SELECT 1, 3 WHERE NOT EXISTS (SELECT 1 FROM flashcard_reviews)")
    c.execute("INSERT INTO battle_history (boss_id, outcome) SELECT 1, 'DEFEAT' WHERE NOT EXISTS (SELECT 1 FROM battle_history)")
    
    conn.commit()
    conn.close()
    print("All tables created successfully.")

if __name__ == "__main__":
    create_missing_tables()
