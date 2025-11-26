import sqlite3

def check_xp_persistence():
    try:
        conn = sqlite3.connect('upsc_saga.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 1. Read initial state
        cursor.execute("SELECT id, current_xp, level, max_xp FROM users WHERE id = 1")
        user = dict(cursor.fetchone())
        print(f"Initial State: {user}")
        
        # 2. Update XP
        new_xp = user['current_xp'] + 50
        print(f"Updating XP to {new_xp}...")
        cursor.execute("UPDATE users SET current_xp = ? WHERE id = 1", (new_xp,))
        conn.commit()
        
        # 3. Read again to verify persistence
        cursor.execute("SELECT id, current_xp, level, max_xp FROM users WHERE id = 1")
        updated_user = dict(cursor.fetchone())
        print(f"Updated State: {updated_user}")
        
        if updated_user['current_xp'] == new_xp:
            print("SUCCESS: XP update persisted.")
        else:
            print("FAILURE: XP update did NOT persist.")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_xp_persistence()
