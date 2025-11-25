import sqlite3
import os
from datetime import datetime, timedelta

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'upsc_saga.db')

def migrate():
    print(f"Migrating database at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create shop_items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shop_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            price INTEGER NOT NULL,
            currency TEXT DEFAULT 'xp',
            icon TEXT,
            duration_hours INTEGER,
            max_uses INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create user_inventory table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            item_id TEXT NOT NULL,
            quantity INTEGER DEFAULT 1,
            purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            activated_at TIMESTAMP,
            expires_at TIMESTAMP,
            FOREIGN KEY (item_id) REFERENCES shop_items(item_id)
        )
    ''')
    
    # Create transactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            item_id TEXT NOT NULL,
            amount INTEGER NOT NULL,
            currency TEXT NOT NULL,
            transaction_type TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (item_id) REFERENCES shop_items(item_id)
        )
    ''')
    
    print("Created shop tables.")
    
    # Seed shop items
    shop_items = [
        # Power-ups (XP/Currency based)
        ('xp_boost_2x', '2x XP Boost', 'Double XP for all activities for 24 hours', 'power-up', 500, 'xp', '⚡', 24, None),
        ('xp_boost_3x', '3x XP Boost', 'Triple XP for all activities for 12 hours', 'power-up', 1000, 'xp', '⚡⚡', 12, None),
        ('hacksilver_multiplier', 'Hacksilver Multiplier', 'Earn 2x Hacksilver for 48 hours', 'power-up', 800, 'xp', '💰', 48, None),
        
        # Streak Protection
        ('streak_freeze', 'Streak Freeze', 'Protects your streak for 1 missed day', 'utility', 300, 'xp', '🛡️', None, 1),
        ('streak_freeze_3pack', 'Streak Freeze (3-Pack)', 'Protects your streak for 3 missed days', 'utility', 750, 'xp', '🛡️🛡️🛡️', None, 3),
        
        # Study Aids
        ('hint_token', 'Hint Token', 'Get a hint on any MCQ question', 'utility', 100, 'xp', '💡', None, 1),
        ('hint_token_5pack', 'Hint Tokens (5-Pack)', 'Get 5 hint tokens', 'utility', 400, 'xp', '💡💡💡', None, 5),
        ('time_extension', 'Time Extension', 'Add 30 minutes to any timed test', 'utility', 200, 'xp', '⏰', None, 1),
        ('auto_save', 'Auto-Save Answers', 'Automatically save answer drafts for 7 days', 'utility', 600, 'xp', '💾', 168, None),
        
        # Challenge Related
        ('challenge_reroll', 'Challenge Reroll', 'Reroll today\'s daily challenge once', 'utility', 150, 'xp', '🔄', None, 1),
        ('challenge_skip', 'Challenge Skip', 'Skip today\'s challenge without breaking streak', 'utility', 250, 'xp', '⏭️', None, 1),
        
        # Cosmetics (Hacksilver based)
        ('theme_dark_ice', 'Dark Ice Theme', 'Cool blue theme for your dashboard', 'cosmetic', 1000, 'hacksilver', '🎨', None, None),
        ('theme_blood_rage', 'Blood Rage Theme', 'Fierce red theme', 'cosmetic', 1000, 'hacksilver', '🎨', None, None),
        ('theme_golden_glory', 'Golden Glory Theme', 'Luxurious gold theme', 'cosmetic', 1500, 'hacksilver', '🎨', None, None),
        ('badge_frame_bronze', 'Bronze Badge Frame', 'Bronze frame for your badges', 'cosmetic', 500, 'hacksilver', '🖼️', None, None),
        ('badge_frame_silver', 'Silver Badge Frame', 'Silver frame for your badges', 'cosmetic', 800, 'hacksilver', '🖼️', None, None),
        ('badge_frame_gold', 'Gold Badge Frame', 'Gold frame for your badges', 'cosmetic', 1200, 'hacksilver', '🖼️', None, None),
        
        # Special Items (Mixed currency)
        ('lucky_charm', 'Lucky Charm', 'Increased chance of critical success for 24h', 'power-up', 2000, 'hacksilver', '🍀', 24, None),
        ('wisdom_scroll', 'Wisdom Scroll', 'Unlock 3 random locked topics', 'utility', 1500, 'xp', '📜', None, 1),
        ('mentor_summon', 'Mentor Summon', 'Get personalized study advice from Mimir', 'utility', 500, 'xp', '👨‍🏫', None, 1),
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO shop_items 
        (item_id, name, description, category, price, currency, icon, duration_hours, max_uses)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', shop_items)
    
    print(f"Seeded {len(shop_items)} shop items.")
    
    conn.commit()
    conn.close()
    print("Migration complete!")

if __name__ == '__main__':
    migrate()
