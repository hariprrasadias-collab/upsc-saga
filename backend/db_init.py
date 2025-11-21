# backend/db_init.py
import sqlite3
import os

DATABASE = 'upsc_saga.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row # This allows access to columns by name
    return conn

def init_db():
    # Remove existing db file if it exists (for fresh start/reset)
    if os.path.exists(DATABASE):
        os.remove(DATABASE)
        print(f"Removed existing database: {DATABASE}")

    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("Initializing database schema...")

    # Create users table
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            level INTEGER DEFAULT 1,
            current_xp INTEGER DEFAULT 0,
            max_xp INTEGER DEFAULT 100,
            strength_stat INTEGER DEFAULT 1,
            runic_stat INTEGER DEFAULT 1,
            vitality_stat INTEGER DEFAULT 1,
            luck_stat INTEGER DEFAULT 1
        )
    ''')
    print("Table 'users' created.")

    # Create tasks table
    cursor.execute('''
        CREATE TABLE tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            xp_reward INTEGER NOT NULL,
            associated_stat TEXT, -- e.g., 'strength_stat', 'runic_stat'
            due_date TEXT NOT NULL, -- YYYY-MM-DD format
            isCompleted INTEGER DEFAULT 0, -- 0 for false, 1 for true
            is_quest INTEGER DEFAULT 0, -- 0 for regular task, 1 for quest
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    print("Table 'tasks' created.")

    # Add a default user
    cursor.execute('''
        INSERT INTO users (username, password, level, current_xp, max_xp, strength_stat, runic_stat, vitality_stat, luck_stat)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', ('hero', 'password', 1, 0, 100, 1, 1, 1, 1))
    print("Default 'hero' user created.")
    
    conn.commit()
    conn.close()
    print("Database initialization complete.")

if __name__ == '__main__':
    init_db()