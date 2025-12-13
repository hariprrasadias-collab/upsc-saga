from flask import Blueprint, jsonify, request, session, current_app
from app.services.badge_service import badge_service

badges_bp = Blueprint('badges', __name__)

def get_current_user_id():
    """
    Helper to get user_id from session with dev fallback.
    Returns None if unauthorized in production.
    """
    user_id = session.get('user_id')
    if user_id:
        return user_id

    # Fallback for development/demo mode
    if current_app.debug or current_app.config.get('FLASK_ENV') == 'development':
        return 1

    return None

@badges_bp.route('/api/badges/all', methods=['GET'])
def get_all_badges():
    """
    Get all badges with unlock status for the current user.
    """
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({'error': 'Unauthorized'}), 401

        badges = badge_service.get_all_badges(user_id)
        return jsonify(badges)
    except Exception as e:
        print(f"Error fetching badges: {e}")
        return jsonify({'error': str(e)}), 500

@badges_bp.route('/api/badges/user', methods=['GET'])
def get_user_badges():
    """
    Get only unlocked badges for the current user.
    """
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({'error': 'Unauthorized'}), 401

        badges = badge_service.get_user_badges(user_id)
        return jsonify(badges)
    except Exception as e:
        print(f"Error fetching user badges: {e}")
        return jsonify({'error': str(e)}), 500

@badges_bp.route('/api/badges/check', methods=['POST'])
def check_badges():
    """
    Manually trigger badge unlock check.
    Returns list of newly unlocked badge IDs.
    """
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({'error': 'Unauthorized'}), 401

        newly_unlocked = badge_service.check_and_unlock_badges(user_id)
        
        # If badges were unlocked, get their details
        if newly_unlocked:
            from app.db import get_db
            conn = get_db()
            
            placeholders = ','.join('?' * len(newly_unlocked))
            unlocked_badges = conn.execute(
                f'SELECT * FROM badges WHERE id IN ({placeholders})',
                newly_unlocked
            ).fetchall()
            
            return jsonify({
                'unlocked_count': len(newly_unlocked),
                'badges': [dict(row) for row in unlocked_badges]
            })
        else:
            return jsonify({
                'unlocked_count': 0,
                'badges': []
            })
            
    except Exception as e:
        print(f"Error checking badges: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@badges_bp.route('/api/badges/progress', methods=['GET'])
def get_badge_progress():
    """
    Get progress toward locked badges.
    """
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({'error': 'Unauthorized'}), 401
        
        from app.db import get_db
        conn = get_db()
        
        progress = conn.execute('''
            SELECT b.id, b.name, b.description, b.icon_url,
                   bp.current_value, bp.target_value,
                   CAST(bp.current_value AS FLOAT) / bp.target_value * 100 as progress_pct
            FROM badges b
            JOIN badge_progress bp ON b.id = bp.badge_id
            WHERE bp.user_id = ?
            AND b.id NOT IN (SELECT badge_id FROM user_badges WHERE user_id = ?)
            ORDER BY progress_pct DESC
        ''', (user_id, user_id)).fetchall()
        
        return jsonify([dict(row) for row in progress])
        
    except Exception as e:
        print(f"Error fetching badge progress: {e}")
        return jsonify({'error': str(e)}), 500
