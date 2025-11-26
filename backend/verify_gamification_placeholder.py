from app.services.game_engine import calculate_and_apply_rewards
from app.db import get_db
import sqlite3

def verify_gamification():
    conn = sqlite3.connect('upsc_saga.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 1. Get current stats
    user = cursor.execute('SELECT * FROM users WHERE id = 1').fetchone()
    print(f"Initial: Level {user['level']}, XP {user['current_xp']}/{user['max_xp']}")
    print(f"Stats: STR {user['strength_stat']}, LUCK {user['luck_stat']}")
    
    initial_level = user['level']
    initial_str = user['strength_stat']
    
    # 2. Grant enough XP to level up
    xp_needed = user['max_xp'] - user['current_xp'] + 10
    print(f"\nGranting {xp_needed} XP...")
    
    # We need to run this within the app context or mock get_db
    # Since we are running as a standalone script, we need to mock get_db or just copy the logic?
    # Better to use the actual function if possible, but it imports get_db from app.db which uses g.
    # Let's just create a temporary route or use a test context.
    # Actually, simpler: I'll just write a script that updates the DB directly using the SAME LOGIC to verify my logic, 
    # OR I can try to import the app and run it.
    
    pass

if __name__ == "__main__":
    # This script is just a placeholder. I will run the verification via a proper app context script.
    pass
