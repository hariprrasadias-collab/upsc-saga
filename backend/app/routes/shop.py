from app.utils.session import get_current_user_id
from flask import Blueprint, request, jsonify
from app.db import get_db

bp = Blueprint('shop', __name__, url_prefix='/api/shop')

@bp.route('/inventory', methods=['GET'])
def get_inventory():
    user_id = get_current_user_id()
    conn = get_db()
    items = conn.execute('SELECT item_id, equipped FROM inventory WHERE user_id = ?', (user_id,)).fetchall()
    user = conn.execute('SELECT hacksilver FROM users WHERE id = ?', (user_id,)).fetchone()
    return jsonify({
        "hacksilver": user['hacksilver'],
        "owned_items": [dict(i) for i in items]
    })

@bp.route('/buy', methods=['POST'])
def buy_item():
    user_id = get_current_user_id()
    data = request.get_json()
    cost = data.get('cost')
    
    if cost < 0:
        return jsonify({"error": "Invalid cost"}), 400

    conn = get_db()
    user = conn.execute('SELECT hacksilver FROM users WHERE id = ?', (user_id,)).fetchone()
    
    if user['hacksilver'] < cost:
        return jsonify({"error": "Not enough Hacksilver"}), 400
        
    # Deduct Money
    conn.execute('UPDATE users SET hacksilver = hacksilver - ? WHERE id = ?', (cost, user_id))
    # Add Item
    conn.execute('INSERT INTO inventory (user_id, item_id, item_name, equipped) VALUES (?, ?, ?, 0)',
                 (user_id, data['item_id'], data['item_name']))
    
    conn.commit()
    return jsonify({"message": "Item Purchased", "new_balance": user['hacksilver'] - cost}), 200
