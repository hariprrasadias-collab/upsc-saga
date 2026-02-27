from flask import Blueprint, request, jsonify
from app.db import get_db

bp = Blueprint('shop', __name__, url_prefix='/api/shop')

# Server-side Catalog (Source of Truth)
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
    if not data:
        return jsonify({"error": "Invalid request body"}), 400

    item_id = data.get('item_id')

    # 1. Validate Item ID
    if not item_id or item_id not in SHOP_CATALOG:
        return jsonify({"error": "Invalid Item ID"}), 400

    # 2. Get Trustworthy Cost & Name from Server Catalog
    item = SHOP_CATALOG[item_id]
    cost = item['cost']
    item_name = item['name']

    conn = get_db()
    user = conn.execute('SELECT hacksilver FROM users WHERE id = ?', (user_id,)).fetchone()
    
    # 3. Check Balance
    if user['hacksilver'] < cost:
        return jsonify({"error": "Not enough Hacksilver"}), 400
        
    # 4. Deduct Money & Add Item
    try:
        conn.execute('UPDATE users SET hacksilver = hacksilver - ? WHERE id = ?', (cost, user_id))
        conn.execute('INSERT INTO inventory (user_id, item_id, item_name, equipped) VALUES (?, ?, ?, 0)',
                     (user_id, item_id, item_name))
        conn.commit()
        return jsonify({"message": "Item Purchased", "new_balance": user['hacksilver'] - cost}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
