from flask import Blueprint, jsonify, request
from app.services.shop_service import shop_service

shop_bp_new = Blueprint('shop_new', __name__)

@shop_bp_new.route('/api/shop/items', methods=['GET'])
def get_shop_items():
    """Get all shop items."""
    try:
        items = shop_service.get_all_items()
        return jsonify(items)
    except Exception as e:
        print(f"Error fetching shop items: {e}")
        return jsonify({'error': str(e)}), 500

@shop_bp_new.route('/api/shop/balance', methods=['GET'])
def get_balance():
    """Get user's currency balance."""
    try:
        user_id = 1  # TODO: Get from session
        balance = shop_service.get_user_balance(user_id)
        return jsonify(balance)
    except Exception as e:
        print(f"Error fetching balance: {e}")
        return jsonify({'error': str(e)}), 500

@shop_bp_new.route('/api/shop/purchase', methods=['POST'])
def purchase_item():
    """Purchase an item."""
    try:
        user_id = 1  # TODO: Get from session
        data = request.get_json()
        item_id = data.get('item_id')
        
        if not item_id:
            return jsonify({'error': 'item_id required'}), 400
        
        result = shop_service.purchase_item(user_id, item_id)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        print(f"Error purchasing item: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@shop_bp_new.route('/api/shop/inventory', methods=['GET'])
def get_inventory():
    """Get user's inventory."""
    try:
        user_id = 1  # TODO: Get from session
        inventory = shop_service.get_user_inventory(user_id)
        return jsonify(inventory)
    except Exception as e:
        print(f"Error fetching inventory: {e}")
        return jsonify({'error': str(e)}), 500

@shop_bp_new.route('/api/shop/activate', methods=['POST'])
def activate_item():
    """Activate an item from inventory."""
    try:
        user_id = 1  # TODO: Get from session
        data = request.get_json()
        inventory_id = data.get('inventory_id')
        
        if not inventory_id:
            return jsonify({'error': 'inventory_id required'}), 400
        
        result = shop_service.activate_item(user_id, inventory_id)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        print(f"Error activating item: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@shop_bp_new.route('/api/shop/active', methods=['GET'])
def get_active_powerups():
    """Get currently active power-ups."""
    try:
        user_id = 1  # TODO: Get from session
        active = shop_service.get_active_powerups(user_id)
        return jsonify(active)
    except Exception as e:
        print(f"Error fetching active power-ups: {e}")
        return jsonify({'error': str(e)}), 500
