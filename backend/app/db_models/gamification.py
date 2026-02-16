from app.db import get_db

def init_gamification_tables():
    """Initialize tables for Gamification (Challenges, Streaks, Rewards)"""
    conn = get_db()
    
    # 1. Challenges Table (The catalog of available challenges)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS challenges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            type TEXT NOT NULL, -- 'daily', 'weekly', 'milestone'
            target_metric TEXT, -- 'hours_studied', 'questions_solved', 'flashcards_reviewed'
            target_value INTEGER DEFAULT 1,
            xp_reward INTEGER DEFAULT 50,
            hacksilver_reward INTEGER DEFAULT 10,
            icon TEXT,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    # 2. User Challenges (Assignments and Progress)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS user_challenges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER DEFAULT 1,
            challenge_id INTEGER,
            assigned_date TEXT NOT NULL, -- YYYY-MM-DD
            progress INTEGER DEFAULT 0,
            completed BOOLEAN DEFAULT 0,
            completed_at TIMESTAMP,
            FOREIGN KEY (challenge_id) REFERENCES challenges (id)
        )
    ''')
    
    # 3. Streaks (Daily Activity Tracking)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS streaks (
            user_id INTEGER PRIMARY KEY,
            current_streak INTEGER DEFAULT 0,
            longest_streak INTEGER DEFAULT 0,
            last_activity_date TEXT -- YYYY-MM-DD
        )
    ''')
    
    # 4. Seed Initial Challenges (if empty)
    existing = conn.execute('SELECT count(*) FROM challenges').fetchone()[0]
    if existing == 0:
        challenges = [
            ('Daily Focus', 'Study for 4 hours today', 'daily', 'hours_studied', 4, 100, 20, 'clock'),
            ('Flashcard Master', 'Review 50 flashcards', 'daily', 'flashcards_reviewed', 50, 50, 10, 'card'),
            ('Answer Writer', 'Write 2 answers today', 'daily', 'answers_written', 2, 150, 30, 'pen'),
            ('Mock Warrior', 'Complete 1 mock test', 'daily', 'mock_tests', 1, 200, 50, 'sword'),
            ('Early Bird', 'Start studying before 6 AM', 'daily', 'start_time', 6, 50, 10, 'sun')
        ]
        conn.executemany('''
            INSERT INTO challenges (title, description, type, target_metric, target_value, xp_reward, hacksilver_reward, icon)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', challenges)
        print("Seeded initial challenges.")
        
    # --- SHOP SYSTEM ---
    # Create shop_items table (Used by Shop Service / New Shop)
    conn.execute('''
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

    # Create user_inventory table (Used by Shop Service / New Shop)
    conn.execute('''
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

    # Seed shop items if empty
    existing_shop = conn.execute('SELECT count(*) FROM shop_items').fetchone()[0]
    if existing_shop == 0:
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

        conn.executemany('''
            INSERT OR IGNORE INTO shop_items
            (item_id, name, description, category, price, currency, icon, duration_hours, max_uses)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', shop_items)
        print(f"Seeded {len(shop_items)} shop items.")

    conn.commit()
