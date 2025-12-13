import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'upsc_saga.db')

def create_table():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    print("🎨 Creating 'visual_gallery' table...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS visual_gallery (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            prompt TEXT,
            seed INTEGER,
            model TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            meta_tags TEXT
        )
    ''')
    
    conn.commit()
    print("✅ Table created successfully.")
    conn.close()

if __name__ == "__main__":
    create_table()
