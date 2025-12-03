"""
API Routes for The Night Watchman
"""
from flask import Blueprint, jsonify, request
from app.services.night_watchman import night_watchman
from app.db_models.night_watchman import get_latest_briefing, mark_briefing_read, init_watchman_tables

watchman_bp = Blueprint('watchman', __name__)
print("🦉 Night Watchman Routes Imported")

@watchman_bp.route('/trigger', methods=['POST'])
def trigger_watchman():
    """Manually trigger the Night Watchman patrol"""
    try:
        result = night_watchman.perform_nightly_watch()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@watchman_bp.route('/latest', methods=['GET'])
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

@watchman_bp.route('/history', methods=['GET'])
def get_history():
    """Get briefing history"""
    try:
        from app.db import get_db
        conn = get_db()
        rows = conn.execute('''
            SELECT id, date, quote, articles_analyzed, is_read 
            FROM morning_briefings 
            ORDER BY date DESC 
            LIMIT 30
        ''').fetchall()
        
        history = [dict(row) for row in rows]
        return jsonify({'success': True, 'history': history})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@watchman_bp.route('/briefing/<int:id>', methods=['GET'])
def get_briefing_by_id(id):
    """Get a specific briefing"""
    try:
        from app.db import get_db
        conn = get_db()
        row = conn.execute('SELECT * FROM morning_briefings WHERE id = ?', (id,)).fetchone()
        
        if row:
            return jsonify({'success': True, 'briefing': dict(row)})
        else:
            return jsonify({'success': False, 'message': 'Briefing not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
