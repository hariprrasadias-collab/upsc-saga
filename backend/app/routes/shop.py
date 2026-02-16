from flask import Blueprint, request, jsonify
from app.db import get_db

bp = Blueprint('shop', __name__, url_prefix='/api/shop')

# 🛡️ Sentinel: Hardcoded catalog to prevent price tampering
# This matches the frontend SHOP_CATALOG in Armory.tsx
SHOP_CATALOG = {
    'leviathan_axe': {'name': 'Leviathan Axe', 'cost': 200},
    'chaos_blades': {'name': 'Blades of Chaos', 'cost': 350},
    'guardian_shield': {'name': 'Guardian Shield', 'cost': 150},
    'mimir_head': {'name': 'Mimir Upgrade', 'cost': 500},
    'spartan_rage': {'name': 'Greater Rage', 'cost': 300}
}

@bp.route('/inventory', methods=['GET'])
def get_inventory():
    user_id = 1
    conn = get_db()
    items = conn.execute('SELECT item_id, equipped FROM inventory WHERE user_id = ?', (user_id,)).fetchall()
    user = conn.execute('SELECT hacksilver FROM users WHERE id = ?', (user_id,)).fetchone()

    hacksilver = user['hacksilver'] if user else 0

    return jsonify({
        "hacksilver": hacksilver,
        "owned_items": [dict(i) for i in items]
    })

@bp.route('/buy', methods=['POST'])
def buy_item():
    user_id = 1
    data = request.get_json()
    
    # 🛡️ Sentinel: Validate input and use server-side pricing
    item_id = data.get('item_id')

    if not item_id or item_id not in SHOP_CATALOG:
        return jsonify({"error": "Invalid item ID"}), 400

    # Get secure price and name from catalog
    item_info = SHOP_CATALOG[item_id]
    real_cost = item_info['cost']
    item_name = item_info['name']

    conn = get_db()
    user = conn.execute('SELECT hacksilver FROM users WHERE id = ?', (user_id,)).fetchone()
    
    if not user:
        return jsonify({"error": "User not found"}), 404

    if user['hacksilver'] < real_cost:
        return jsonify({"error": f"Not enough Hacksilver. Need {real_cost}"}), 400
        
    # Check if already owned to prevent duplicates (Frontend treats them as unique)
    existing = conn.execute('SELECT 1 FROM inventory WHERE user_id = ? AND item_id = ?', (user_id, item_id)).fetchone()
    if existing:
        return jsonify({"error": "Item already owned"}), 400

    # Deduct Money using real cost
    conn.execute('UPDATE users SET hacksilver = hacksilver - ? WHERE id = ?', (real_cost, user_id))

    # Add Item
    conn.execute('INSERT INTO inventory (user_id, item_id, item_name, equipped) VALUES (?, ?, ?, 0)',
                 (user_id, item_id, item_name))
    
    conn.commit()
    return jsonify({"message": "Item Purchased", "new_balance": user['hacksilver'] - real_cost}), 200
