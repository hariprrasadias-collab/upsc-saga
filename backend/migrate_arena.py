import sqlite3
import os

# Database path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'upsc_saga.db')

def migrate():
    print(f"Migrating database at {DATABASE}...")
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Create boss_battles table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS boss_battles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        boss_name TEXT NOT NULL,
        subject TEXT NOT NULL,
        total_hp INTEGER NOT NULL,
        difficulty TEXT NOT NULL,
        description TEXT,
        image_url TEXT
    )
    ''')
    print("Created boss_battles table.")

    # Create battle_history table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS battle_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        boss_id INTEGER NOT NULL,
        damage_dealt INTEGER DEFAULT 0,
        damage_taken INTEGER DEFAULT 0,
        outcome TEXT,
        loot_earned TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (boss_id) REFERENCES boss_battles (id)
    )
    ''')
    print("Created battle_history table.")

    # Seed initial bosses
    bosses = [
        ('Polity Titan', 'Polity', 10, 'Hard', 'A colossus made of granite and constitutional amendments.', '/assets/bosses/polity_titan.png'),
        ('History Warlord', 'History', 10, 'Medium', 'An ancient conqueror who knows every date and battle.', '/assets/bosses/history_warlord.png'),
        ('Economy Dragon', 'Economy', 10, 'Hard', 'A greedy dragon hoarding concepts of GDP and inflation.', '/assets/bosses/economy_dragon.png'),
        ('Geography Golem', 'Geography', 10, 'Medium', 'A shifting mass of tectonic plates and river systems.', '/assets/bosses/geography_golem.png'),
        ('Science Specter', 'Science', 10, 'Easy', 'An ethereal being of pure energy and biological processes.', '/assets/bosses/science_specter.png'),
        # New Bosses
        ('Terra Titan', 'Geography', 15, 'Hard', 'The embodiment of physical geography, commanding mountains and oceans.', '/assets/bosses/terra_titan.png'),
        ('Map Maven', 'Geography', 12, 'Medium', 'A master cartographer who tests your knowledge of locations and borders.', '/assets/bosses/map_maven.png'),
        ('Fiscal Phantom', 'Economy', 15, 'Hard', 'A ghostly figure haunting the corridors of the Budget and Economic Survey.', '/assets/bosses/fiscal_phantom.png'),
        ('Macro Monarch', 'Economy', 12, 'Medium', 'A ruler of macroeconomic concepts and banking systems.', '/assets/bosses/macro_monarch.png'),
        ('Gaia Guardian', 'Environment', 15, 'Hard', 'Protector of biodiversity and ecological balance.', '/assets/bosses/gaia_guardian.png'),
        ('Climate Colossus', 'Environment', 12, 'Medium', 'A storm giant representing climate change and international treaties.', '/assets/bosses/climate_colossus.png'),
        ('Tech Titan', 'Science', 15, 'Hard', 'A cyborg entity fused with emerging technologies like AI and Blockchain.', '/assets/bosses/tech_titan.png'),
        ('Bio Behemoth', 'Science', 12, 'Medium', 'A massive creature evolved from pure biological sciences.', '/assets/bosses/bio_behemoth.png')
    ]

    for boss in bosses:
        # Check if boss exists
        cursor.execute('SELECT id FROM boss_battles WHERE boss_name = ?', (boss[0],))
        if not cursor.fetchone():
            cursor.execute('''
            INSERT INTO boss_battles (boss_name, subject, total_hp, difficulty, description, image_url)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', boss)
            print(f"Seeded boss: {boss[0]}")

    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == '__main__':
    migrate()
