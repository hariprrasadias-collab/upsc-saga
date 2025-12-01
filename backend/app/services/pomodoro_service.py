from app.db import get_db
from datetime import datetime

class PomodoroService:
    @staticmethod
    def log_session(duration, xp_awarded=50):
        """Log a completed session and update XP."""
        conn = get_db()
        c = conn.cursor()
        timestamp = datetime.now().isoformat()
        
        try:
            # Log session
            c.execute('''
                INSERT INTO pomodoro_sessions (timestamp, duration, xp_awarded)
                VALUES (?, ?, ?)
            ''', (timestamp, duration, xp_awarded))
            
            # Update XP
            c.execute('''
                UPDATE user_profile 
                SET current_xp = current_xp + ?
                WHERE user_id = 1
            ''', (xp_awarded,))
            
            # Check Level Up
            c.execute('SELECT current_xp, level FROM user_profile WHERE user_id = 1')
            user = c.fetchone()
            current_xp = user['current_xp']
            current_level = user['level']
            max_xp = current_level * 100
            
            level_up = False
            new_level = current_level
            
            if current_xp >= max_xp:
                new_level = current_level + 1
                c.execute('''
                    UPDATE user_profile 
                    SET level = ?, current_xp = ?
                    WHERE user_id = 1
                ''', (new_level, current_xp - max_xp))
                level_up = True
                
            conn.commit()
            return {
                'success': True,
                'xp_awarded': xp_awarded,
                'level_up': level_up,
                'new_level': new_level
            }
        except Exception as e:
            conn.rollback()
            raise e
        # finally block removed to keep connection open for request context

    @staticmethod
    def get_stats_today():
        """Get stats for today."""
        conn = get_db()
        c = conn.cursor()
        today = datetime.now().date().isoformat()
        
        c.execute('''
            SELECT COUNT(*) as sessions_today, SUM(xp_awarded) as xp_today
            FROM pomodoro_sessions
            WHERE DATE(timestamp) = ?
        ''', (today,))
        
        stats = c.fetchone()
        # conn.close() removed
        
        return {
            'sessions_today': stats['sessions_today'] or 0,
            'xp_today': stats['xp_today'] or 0
        }

    @staticmethod
    def get_brain_context():
        """Standard interface for the Brain to pull context."""
        stats = PomodoroService.get_stats_today()
        return {
            "status": "active",
            "data": {
                "focus_sessions": stats['sessions_today'],
                "xp_earned": stats['xp_today']
            }
        }

# Register Synapse
try:
    from app.services.synapse_registry import SynapseRegistry
    SynapseRegistry.get_instance().register_synapse(
        category='CORE',
        name='pomodoro',
        service_ref=PomodoroService,
        description='Tracks focus sessions and productivity stats.'
    )
except ImportError:
    pass
