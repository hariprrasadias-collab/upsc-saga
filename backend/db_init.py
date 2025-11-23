# backend/db_init.py
import sqlite3
import os  # <--- This was missing

DATABASE = 'upsc_saga.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    # Remove existing database to apply new schema
    if os.path.exists(DATABASE):
        os.remove(DATABASE)
        print(f"Removed existing database: {DATABASE}")

    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("Initializing database schema...")

    # 1. Users (With hacksilver)
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            level INTEGER DEFAULT 1,
            current_xp INTEGER DEFAULT 0,
            max_xp INTEGER DEFAULT 100,
            hacksilver INTEGER DEFAULT 50, -- Starting Money
            strength_stat INTEGER DEFAULT 1,
            runic_stat INTEGER DEFAULT 1,
            vitality_stat INTEGER DEFAULT 1,
            luck_stat INTEGER DEFAULT 1
        )
    ''')

    # 2. Tasks
    cursor.execute('''
        CREATE TABLE tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            xp_reward INTEGER NOT NULL,
            associated_stat TEXT,
            due_date TEXT NOT NULL,
            isCompleted INTEGER DEFAULT 0,
            is_quest INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # 3. Codex Progress
    cursor.execute('''
        CREATE TABLE user_progress (
            user_id INTEGER NOT NULL,
            node_id TEXT NOT NULL,
            status TEXT NOT NULL,
            PRIMARY KEY (user_id, node_id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # 4. Lore Tablets (Notes)
    cursor.execute('''
        CREATE TABLE lore_tablets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # 5. Mock Tests
    cursor.execute('''
        CREATE TABLE mock_tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            boss_name TEXT NOT NULL,
            subject TEXT NOT NULL,
            total_marks INTEGER NOT NULL,
            cutoff_marks INTEGER NOT NULL,
            my_score REAL NOT NULL,
            date_fought TEXT DEFAULT CURRENT_TIMESTAMP,
            is_victory INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # 6. Mimir's History
    cursor.execute('''
        CREATE TABLE mimir_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            sender TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # 7. Inventory (Shop Items)
    cursor.execute('''
        CREATE TABLE inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            item_id TEXT NOT NULL,
            item_name TEXT NOT NULL,
            equipped INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    print("Table 'inventory' created.")

    # Create Default User
    cursor.execute('''
        INSERT INTO users (username, password, level, current_xp, max_xp, hacksilver, strength_stat, runic_stat, vitality_stat, luck_stat)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', ('hero', 'password', 1, 0, 100, 50, 1, 1, 1, 1))
    
    conn.commit()
    conn.close()
    print("Database initialization complete.")

if __name__ == '__main__':
    init_db()