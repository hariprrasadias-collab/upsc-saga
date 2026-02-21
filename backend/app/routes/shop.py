from flask import Blueprint, request, jsonify
from app.db import get_db

bp = Blueprint('shop', __name__, url_prefix='/api/shop')

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

# Security: Server-side catalog to prevent price tampering
SHOP_CATALOG = {
    'leviathan_axe': {'name': 'Leviathan Axe', 'cost': 200},
    'chaos_blades': {'name': 'Blades of Chaos', 'cost': 350},
    'guardian_shield': {'name': 'Guardian Shield', 'cost': 150},
    'mimir_head': {'name': 'Mimir Upgrade', 'cost': 500},
    'spartan_rage': {'name': 'Greater Rage', 'cost': 300}
}

@bp.route('/buy', methods=['POST'])
def buy_item():
    user_id = 1
    data = request.get_json()
    item_id = data.get('item_id')
    
    if not item_id or item_id not in SHOP_CATALOG:
        return jsonify({"error": "Invalid item or item not found in catalog"}), 400

    # Look up cost and name from the secure catalog
    item = SHOP_CATALOG[item_id]
    cost = item['cost']
    item_name = item['name']

    conn = get_db()
    user = conn.execute('SELECT hacksilver FROM users WHERE id = ?', (user_id,)).fetchone()
    
    if user['hacksilver'] < cost:
        return jsonify({"error": "Not enough Hacksilver"}), 400
        
    # Deduct Money
    conn.execute('UPDATE users SET hacksilver = hacksilver - ? WHERE id = ?', (cost, user_id))
    # Add Item
    conn.execute('INSERT INTO inventory (user_id, item_id, item_name, equipped) VALUES (?, ?, ?, 0)',
                 (user_id, item_id, item_name))
    
    conn.commit()
    return jsonify({"message": "Item Purchased", "new_balance": user['hacksilver'] - cost}), 200
