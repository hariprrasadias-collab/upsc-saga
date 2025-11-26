from app import create_app
from app.services.game_engine import calculate_and_apply_rewards
from app.db import get_db

app = create_app()

with app.app_context():
    conn = get_db()
    cursor = conn.cursor()
    
    # 1. Get current stats
    user = cursor.execute('SELECT * FROM users WHERE id = 1').fetchone()
    print(f"Initial: Level {user['level']}, XP {user['current_xp']}/{user['max_xp']}")
    print(f"Stats: STR {user['strength_stat']}, LUCK {user['luck_stat']}")
    
    initial_level = user['level']
    initial_str = user['strength_stat']
    
    # 2. Grant enough XP to level up
    xp_needed = user['max_xp'] - user['current_xp'] + 50
    print(f"\nGranting {xp_needed} XP...")
    
    rewards = calculate_and_apply_rewards(1, xp_needed, 10, ['test'])
    print("Rewards:", rewards)
    
    # 3. Check new stats
    user_new = cursor.execute('SELECT * FROM users WHERE id = 1').fetchone()
    print(f"\nFinal: Level {user_new['level']}, XP {user_new['current_xp']}/{user_new['max_xp']}")
    print(f"Stats: STR {user_new['strength_stat']}, LUCK {user_new['luck_stat']}")
    
    if user_new['level'] > initial_level:
        print("✅ Level Up Successful")
        if user_new['strength_stat'] > initial_str:
            print("✅ Stats Increased")
        else:
            print("❌ Stats DID NOT Increase")
    else:
        print("❌ Did not level up (might need more XP)")
