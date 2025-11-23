# Migration script to add calendar_event_metadata table
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'upsc_saga.db')
conn = sqlite3.connect(db_path)

print("Creating calendar_event_metadata table...")

conn.execute('''
    CREATE TABLE IF NOT EXISTS calendar_event_metadata (
        event_id TEXT PRIMARY KEY,
        user_id INTEGER NOT NULL,
        xp_reward INTEGER DEFAULT 0,
        associated_stat TEXT,
        is_completed BOOLEAN DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
''')

conn.commit()
print("✅ calendar_event_metadata table created successfully!")

# Also add timezone to users table if it doesn't exist
try:
    conn.execute('ALTER TABLE users ADD COLUMN timezone TEXT DEFAULT "Asia/Kolkata"')
    conn.commit()
    print("✅ Added timezone column to users table!")
except sqlite3.OperationalError:
    print("ℹ️  Timezone column already exists in users table")

conn.close()
print("\n🎉 Migration completed successfully!")
