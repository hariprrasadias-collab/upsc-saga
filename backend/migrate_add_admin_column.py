import sqlite3
import os

# Point to backend/upsc_saga.db
DB_PATH = os.path.join(os.path.dirname(__file__), 'upsc_saga.db')

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    print(f"Connecting to {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

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
            # Check if table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            if not cursor.fetchone():
                print("Table 'users' does not exist!")
    else:
        print("is_admin column already exists.")

    # Set user 1 as admin
    print("Setting user_id=1 as admin...")
    try:
        cursor.execute("UPDATE users SET is_admin = 1 WHERE id = 1")
        if cursor.rowcount == 0:
            print("User ID 1 not found. Creating it...")
            # Create user 1 if not exists (fallback)
            cursor.execute('''
                INSERT INTO users (id, username, current_xp, level, max_xp, hacksilver, is_admin)
                VALUES (1, 'Hero', 0, 1, 100, 50, 1)
            ''')
            print("Created Admin User (Hero, ID 1)")
        conn.commit()
        print("User 1 set as admin.")
    except Exception as e:
        print(f"Error updating/creating admin user: {e}")

    conn.close()

if __name__ == "__main__":
    migrate()
