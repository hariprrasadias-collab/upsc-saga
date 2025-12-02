"""
API Routes for The Night Watchman
"""
from flask import Blueprint, jsonify, request
from app.services.night_watchman import night_watchman
from app.db_models.night_watchman import get_latest_briefing, mark_briefing_read, init_watchman_tables

watchman_bp = Blueprint('watchman', __name__)

@watchman_bp.route('/trigger', methods=['POST'])
def trigger_watchman():
    """Manually trigger the Night Watchman patrol"""
    try:
        result = night_watchman.perform_nightly_watch()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@watchman_bp.route('/briefing/latest', methods=['GET'])
def get_briefing():
    """Get the latest morning briefing"""
    try:
        briefing = get_latest_briefing()
        if briefing:
            return jsonify({'success': True, 'briefing': briefing})
        else:
            return jsonify({'success': False, 'message': 'No briefing found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@watchman_bp.route('/briefing/<int:id>/read', methods=['POST'])
def mark_read(id):
    """Mark a briefing as read"""
    try:
        mark_briefing_read(id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
