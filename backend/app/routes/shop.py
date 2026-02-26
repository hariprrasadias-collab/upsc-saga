from flask import Blueprint, request, jsonify
from app.db import get_db

bp = Blueprint('shop', __name__, url_prefix='/api/shop')

# Server-side Catalog (Single Source of Truth) to prevent price tampering
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
    return jsonify({
        "hacksilver": user['hacksilver'],
        "owned_items": [dict(i) for i in items]
    })

@bp.route('/buy', methods=['POST'])
def buy_item():
    user_id = 1
    data = request.get_json()
    item_id = data.get('item_id')
    
    # 1. Validate Item exists
    if item_id not in SHOP_CATALOG:
        return jsonify({"error": "Invalid Item ID"}), 400

    # 2. Get Truth from Catalog (Ignore client-provided cost/name)
    item = SHOP_CATALOG[item_id]
    real_cost = item['cost']
    real_name = item['name']

    conn = get_db()
    user = conn.execute('SELECT hacksilver FROM users WHERE id = ?', (user_id,)).fetchone()
    
    # 3. Check Balance against Real Cost
    if user['hacksilver'] < real_cost:
        return jsonify({"error": f"Not enough Hacksilver. Need {real_cost}"}), 400
        
    # 4. Deduct Money
    conn.execute('UPDATE users SET hacksilver = hacksilver - ? WHERE id = ?', (real_cost, user_id))

    # 5. Add Item (using trusted name)
    conn.execute('INSERT INTO inventory (user_id, item_id, item_name, equipped) VALUES (?, ?, ?, 0)',
                 (user_id, item_id, real_name))
    
    conn.commit()
    return jsonify({"message": "Item Purchased", "new_balance": user['hacksilver'] - real_cost}), 200
