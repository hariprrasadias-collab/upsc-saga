from app.utils.session import get_current_user_id
from flask import Blueprint, jsonify, request, session
from app.services.challenge_service import challenge_service

challenges_bp = Blueprint('challenges', __name__)

def get_current_user_id():
    """
    Retrieve the logged-in user's ID from the session.
    Falls back to User ID 1 for development/single-user environments.
    """
    user_id = session.get('user_id')
    if not user_id:
        # Defaults to 1 for single-user mode
        user_id = 1
    return user_id

@challenges_bp.route('/api/challenges/daily', methods=['GET'])
def get_daily_challenge():
    """
    Get today's assigned challenge for the user.
    """
    try:
        user_id = get_current_user_id()
        challenge = challenge_service.get_daily_challenge(user_id)
        
        if not challenge:
            return jsonify({'error': 'No challenge available'}), 404
        
        return jsonify(challenge)
    except Exception as e:
        print(f"Error fetching daily challenge: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@challenges_bp.route('/api/challenges/complete', methods=['POST'])
def complete_challenge():
    """
    Mark today's challenge as complete.
    """
    try:
        user_id = get_current_user_id()
        result = challenge_service.complete_challenge(user_id)
        
        return jsonify(result)
    except Exception as e:
        print(f"Error completing challenge: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@challenges_bp.route('/api/challenges/streak', methods=['GET'])
def get_streak():
    """
    Get user's current streak information.
    """
    try:
        user_id = get_current_user_id()
        streak = challenge_service.get_streak(user_id)
        
        if not streak:
            return jsonify({
                'current_streak': 0,
                'longest_streak': 0,
                'last_activity_date': None
            })
        
        return jsonify(streak)
    except Exception as e:
        print(f"Error fetching streak: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@challenges_bp.route('/api/challenges/history', methods=['GET'])
def get_history():
    """
    Get user's challenge completion history (last 30 days).
    """
    try:
        user_id = get_current_user_id()
        days = request.args.get('days', 30, type=int)
        
        history = challenge_service.get_challenge_history(user_id, days)
        return jsonify(history)
    except Exception as e:
        print(f"Error fetching challenge history: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@challenges_bp.route('/api/challenges/progress', methods=['POST'])
def update_progress():
    """
    Update progress for today's challenge.
    """
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        progress = data.get('progress', 0)
        
        success = challenge_service.update_challenge_progress(user_id, progress)
        
        if success:
            return jsonify({'success': True, 'message': 'Progress updated'})
        else:
            return jsonify({'success': False, 'message': 'No active challenge'}), 404
            
    except Exception as e:
        print(f"Error updating progress: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
