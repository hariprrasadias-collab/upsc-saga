from flask import Blueprint, request, jsonify
from app.db import get_db

bp = Blueprint('shop', __name__, url_prefix='/api/shop')

# Hardcoded catalog to prevent price manipulation
# Matches frontend/src/components/Armory/Armory.tsx
SHOP_CATALOG = {
    'leviathan_axe': 200,
    'chaos_blades': 350,
    'guardian_shield': 150,
    'mimir_head': 500,
    'spartan_rage': 300
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

    if item_id not in SHOP_CATALOG:
        return jsonify({"error": "Invalid item"}), 400
    
    cost = SHOP_CATALOG[item_id]

    conn = get_db()
    user = conn.execute('SELECT hacksilver FROM users WHERE id = ?', (user_id,)).fetchone()
    
    if user['hacksilver'] < cost:
        return jsonify({"error": "Not enough Hacksilver"}), 400
        
    # Deduct Money
    conn.execute('UPDATE users SET hacksilver = hacksilver - ? WHERE id = ?', (cost, user_id))
    # Add Item
    conn.execute('INSERT INTO inventory (user_id, item_id, item_name, equipped) VALUES (?, ?, ?, 0)',
                 (user_id, item_id, data.get('item_name', 'Unknown Item')))
    
    conn.commit()
    return jsonify({"message": "Item Purchased", "new_balance": user['hacksilver'] - cost}), 200
