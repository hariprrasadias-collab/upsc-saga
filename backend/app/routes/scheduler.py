from flask import Blueprint, jsonify, request
from app.services.scheduler import SchedulerService

bp = Blueprint('scheduler', __name__, url_prefix='/api/scheduler')

@bp.route('/due', methods=['GET'])
def get_due_items():
    """Get all items due for revision today"""
    try:
        items = SchedulerService.get_due_items()
        return jsonify(items)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/review', methods=['POST'])
def submit_review():
    """Submit a review rating for an item"""
    data = request.get_json()
    item_type = data.get('item_type')
    item_id = data.get('item_id')
    rating = data.get('rating') # 1-5

    if not all([item_type, item_id, rating]):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        result = SchedulerService.schedule_review(item_type, item_id, rating)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/schedule', methods=['POST'])
def schedule_new_item():
    """Manually schedule a new item for review"""
    data = request.get_json()
    item_type = data.get('item_type')
    item_id = data.get('item_id')
    
    if not all([item_type, item_id]):
        return jsonify({'error': 'Missing required fields'}), 400
        
    try:
        # Default rating of 3 (Good) to start the cycle
        result = SchedulerService.schedule_review(item_type, item_id, 3)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
