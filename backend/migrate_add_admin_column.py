import sqlite3
import os

# Script is in backend/
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Allow overriding DB path via env var (for Fly.io volume / Render persistent disk)
DB_PATH = os.environ.get('DATABASE_PATH', os.path.join(BASE_DIR, 'upsc_saga.db'))

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}. Skipping migration.")
        return

    print(f"Connecting to database at {DB_PATH}")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("Users table does not exist! Creating it...")
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT,
                    password_hash TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    current_xp INTEGER DEFAULT 0,
                    level INTEGER DEFAULT 1,
                    max_xp INTEGER DEFAULT 100,
                    hacksilver INTEGER DEFAULT 0,
                    strength_stat INTEGER DEFAULT 1,
                    runic_stat INTEGER DEFAULT 1,
                    vitality_stat INTEGER DEFAULT 1,
                    luck_stat INTEGER DEFAULT 1
                )
            ''')

        # Check if is_admin column exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [info[1] for info in cursor.fetchall()]

        if 'is_admin' not in columns:
            print("Adding is_admin column to users table...")
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0")
                print("Column added successfully.")
            except sqlite3.OperationalError as e:
                print(f"Error adding column: {e}")
                return
        else:
            print("is_admin column already exists.")

        # Ensure user 1 exists
        cursor.execute("SELECT id FROM users WHERE id = 1")
        if not cursor.fetchone():
            print("User 1 does not exist. Creating default admin user...")
            cursor.execute('''
                INSERT INTO users (id, username, current_xp, level, max_xp, hacksilver, is_admin)
                VALUES (1, 'Hero', 0, 1, 100, 50, 1)
            ''')
        else:
            # Set user 1 as admin
            print("Setting user_id=1 as admin...")
            cursor.execute("UPDATE users SET is_admin = 1 WHERE id = 1")

        conn.commit()
        print("User 1 set as admin.")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    migrate()
