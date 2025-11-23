from app.db import get_db

def award_xp(user_id, xp_amount, hacksilver_amount=0):
    """
    Awards XP and Hacksilver to the user.
    Handles level up logic.
    """
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    
    if not user:
        return False
        
    print(f"DEBUG: Awarding {xp_amount} XP to user {user_id}. Current: {user['current_xp']}")
    current_xp = user['current_xp'] + xp_amount
    max_xp = user['max_xp']
    level = user['level']
    hacksilver = user['hacksilver'] + hacksilver_amount
    
    # Level Up Logic
    while current_xp >= max_xp:
        current_xp -= max_xp
        level += 1
        max_xp = int(max_xp * 1.2) # 20% increase per level
        
    conn.execute('''
        UPDATE users 
        SET level = ?, current_xp = ?, max_xp = ?, hacksilver = ?
        WHERE id = ?
    ''', (level, current_xp, max_xp, hacksilver, user_id))
    
    conn.commit()
    return True
