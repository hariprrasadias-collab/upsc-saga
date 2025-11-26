import random
from app.db import get_db

def calculate_and_apply_rewards(user_id, base_xp, base_hs, tags=[]):
    """
    Central function to calculate XP, Hacksilver, apply Item Buffs, 
    handle Luck criticals, and update Level.
    """
    conn = get_db()
    cursor = conn.cursor()
    
    # 1. Fetch User & Inventory
    user = cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    inv_rows = cursor.execute('SELECT item_id FROM inventory WHERE user_id = ?', (user_id,)).fetchall()
    owned_items = {row['item_id'] for row in inv_rows}
    
    # 2. Check Item Buffs (Multipliers)
    xp_multiplier = 1.0
    
    # Leviathan Axe: Buffs History/Culture
    if 'leviathan_axe' in owned_items:
        if any(t in tags for t in ['history', 'culture', 'ancient', 'medieval', 'modern', 'art']):
            xp_multiplier += 0.20 # +20%
            
    # Blades of Chaos: Buffs Polity/Law
    if 'chaos_blades' in owned_items:
        if any(t in tags for t in ['polity', 'constitution', 'law', 'governance', 'rights']):
            xp_multiplier += 0.20 # +20%
            
    final_xp = int(base_xp * xp_multiplier)
    
    # 3. Calculate Hacksilver (Random Variation)
    # e.g., if base_hs is 100, gives between 90 and 110.
    variance = int(base_hs * 0.1) if base_hs > 0 else 0
    final_hs = random.randint(max(1, base_hs - variance), base_hs + variance)

    # 4. Check Luck Stat (Critical Hit)
    # 2% Chance per Luck point. Cap at 50%.
    crit_chance = min(user['luck_stat'] * 2, 50)
    roll = random.randint(1, 100)
    is_crit = roll <= crit_chance
    
    if is_crit:
        final_xp *= 2
        final_hs *= 2  # Double Money too!
        
    # 5. Apply to User (Level Up Logic)
    current_xp = user['current_xp'] + final_xp
    current_hs = user['hacksilver'] + final_hs
    level = user['level']
    max_xp = user['max_xp']
    
    # Stats
    strength = user['strength_stat']
    intellect = user['runic_stat'] # Mapping runic to intellect for clarity if needed, or keeping as runic
    vitality = user['vitality_stat']
    luck = user['luck_stat']
    
    leveled_up = False
    while current_xp >= max_xp:
        level += 1
        current_xp -= max_xp
        max_xp = round(max_xp * 1.2) # XP curve gets harder
        leveled_up = True
        
        # Increase Stats on Level Up
        strength += 1
        intellect += 1
        vitality += 1
        luck += 1
        
    # 6. Save to DB
    cursor.execute('''
        UPDATE users 
        SET current_xp = ?, level = ?, max_xp = ?, hacksilver = ?,
            strength_stat = ?, runic_stat = ?, vitality_stat = ?, luck_stat = ?
        WHERE id = ?
    ''', (current_xp, level, max_xp, current_hs, strength, intellect, vitality, luck, user_id))
    
    conn.commit()
    
    return {
        "xp_gained": final_xp,
        "hs_gained": final_hs,
        "is_crit": is_crit,
        "leveled_up": leveled_up,
        "new_balance": current_hs
    }
