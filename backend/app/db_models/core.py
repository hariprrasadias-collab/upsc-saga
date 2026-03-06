from app.db import get_db

def init_core_tables():
    """Initialize core application tables (Users, etc.)"""
    conn = get_db()
    
    # Users Table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT,
            password_hash TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            -- Gamification Stats
            current_xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            max_xp INTEGER DEFAULT 100,
            hacksilver INTEGER DEFAULT 0,
            
            -- RPG Stats
            strength_stat INTEGER DEFAULT 1,
            runic_stat INTEGER DEFAULT 1,
            vitality_stat INTEGER DEFAULT 1,
            luck_stat INTEGER DEFAULT 1,

            -- Admin Role
            is_admin BOOLEAN DEFAULT 0
        )
    ''')
    
    # Inventory Table (for items like Leviathan Axe)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            item_id TEXT NOT NULL, -- 'leviathan_axe', 'chaos_blades'
            item_name TEXT,
            equipped INTEGER DEFAULT 0,
            acquired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Migration for existing inventory table (if missing columns)
    try:
        conn.execute('SELECT item_name FROM inventory LIMIT 1')
    except Exception:
        print("Migrating inventory table: Adding item_name and equipped columns...")
        try:
            conn.execute('ALTER TABLE inventory ADD COLUMN item_name TEXT')
            conn.execute('ALTER TABLE inventory ADD COLUMN equipped INTEGER DEFAULT 0')
            print("Migration successful.")
        except Exception as e:
            print(f"Migration failed: {e}")
    
    # Activity Log Table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER DEFAULT 1,
            activity_type TEXT NOT NULL,
            description TEXT,
            xp_awarded INTEGER DEFAULT 0,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Seed default user if not exists
    existing = conn.execute('SELECT count(*) FROM users').fetchone()[0]
    if existing == 0:
        conn.execute('''
            INSERT INTO users (username, current_xp, level, max_xp, hacksilver, strength_stat, runic_stat, vitality_stat, luck_stat)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('Hero', 0, 1, 100, 50, 5, 5, 5, 5))
        print("Seeded default user 'Hero'.")
        
    conn.commit()
