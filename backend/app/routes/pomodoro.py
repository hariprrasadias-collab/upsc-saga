# app/routes/pomodoro.py
from flask import Blueprint, request, jsonify
from app.db import get_db
from datetime import datetime

pomodoro_bp = Blueprint('pomodoro', __name__)

@pomodoro_bp.route('/api/pomodoro/complete', methods=['POST'])
def complete_pomodoro():
    """
    Log completed Pomodoro session and award XP
    """
    data = request.get_json()
    duration = data.get('duration', 1500)  # Default 25 minutes
    timestamp = data.get('timestamp', datetime.now().isoformat())
    
    conn = get_db()
    c = conn.cursor()
    
    # Award 50 XP for completed Pomodoro
    xp_awarded = 50
    
    try:
        # Log the Pomodoro session
        c.execute('''
            INSERT INTO pomodoro_sessions (timestamp, duration, xp_awarded)
            VALUES (?, ?, ?)
        ''', (timestamp, duration, xp_awarded))
        
        # Update user XP
        c.execute('''
            UPDATE user_profile 
            SET current_xp = current_xp + ?
            WHERE user_id = 1
        ''', (xp_awarded,))
        
        # Check if level up needed
        c.execute('SELECT current_xp, level FROM user_profile WHERE user_id = 1')
        user = c.fetchone()
        current_xp = user['current_xp']
        current_level = user['level']
        
        # Simple level formula: 100 XP per level
        max_xp = current_level * 100
        
        if current_xp >= max_xp:
            new_level = current_level + 1
            c.execute('''
                UPDATE user_profile 
                SET level = ?, current_xp = ?
                WHERE user_id = 1
            ''', (new_level, current_xp - max_xp))
            
            conn.commit()
            conn.close()
            
            return jsonify({
                'success': True,
                'xp_awarded': xp_awarded,
                'level_up': True,
                'new_level': new_level
            })
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'xp_awarded': xp_awarded,
            'level_up': False
        })
        
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'error': str(e)}), 500


@pomodoro_bp.route('/api/pomodoro/stats', methods=['GET'])
def get_pomodoro_stats():
    """
    Get Pomodoro statistics for today
    """
    conn = get_db()
    c = conn.cursor()
    
    today = datetime.now().date().isoformat()
    
    c.execute('''
        SELECT COUNT(*) as sessions_today, SUM(xp_awarded) as xp_today
        FROM pomodoro_sessions
        WHERE DATE(timestamp) = ?
    ''', (today,))
    
    stats = c.fetchone()
    conn.close()
    
    return jsonify({
        'sessions_today': stats['sessions_today'] or 0,
        'xp_today': stats['xp_today'] or 0
    })
