from app.db import get_db
from datetime import datetime

class PomodoroService:
    @staticmethod
    def log_session(duration, xp_awarded=50):
        """Log a completed session and update XP."""
        conn = get_db()
        timestamp = datetime.now().isoformat()
        
        try:
            # Log session
            conn.execute('''
                INSERT INTO pomodoro_sessions (timestamp, duration, xp_awarded, user_id)
                VALUES (?, ?, ?, 1)
            ''', (timestamp, duration, xp_awarded))
            
            # Update XP
            conn.execute('''
                UPDATE user_profile 
                SET current_xp = current_xp + ?
                WHERE user_id = 1
            ''', (xp_awarded,))
            
            # Check Level Up
            row = conn.execute('SELECT current_xp, level FROM user_profile WHERE user_id = 1').fetchone()
            
            level_up = False
            new_level = 1
            
            if row:
                current_xp = row['current_xp']
                current_level = row['level']
                max_xp = current_level * 100

                new_level = current_level

                if current_xp >= max_xp:
                    new_level = current_level + 1
                    conn.execute('''
                        UPDATE user_profile
                        SET level = ?, current_xp = ?
                        WHERE user_id = 1
                    ''', (new_level, current_xp - max_xp))
                    level_up = True
            else:
                # Handle missing user profile (create default)
                try:
                    conn.execute('INSERT INTO user_profile (user_id, current_xp, level) VALUES (1, 0, 1)')
                except:
                    pass # Ignore if exists or other error
                
            conn.commit()
            return {
                'success': True,
                'xp_awarded': xp_awarded,
                'level_up': level_up,
                'new_level': new_level
            }
        except Exception as e:
            conn.rollback()
            print(f"Pomodoro Logging Failed: {e}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def get_stats_today():
        """Get stats for today."""
        try:
            conn = get_db()
            today = datetime.now().date().isoformat()

            row = conn.execute('''
                SELECT COUNT(*) as sessions_today, SUM(xp_awarded) as xp_today
                FROM pomodoro_sessions
                WHERE DATE(timestamp) = ?
            ''', (today,)).fetchone()

            return {
                'sessions_today': row['sessions_today'] or 0,
                'xp_today': row['xp_today'] or 0
            }
        except Exception:
            return {'sessions_today': 0, 'xp_today': 0}

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

    @staticmethod
    def get_break_briefing():
        """
        PHASE 9: FOCUS WHISPER (Drill Sergeant Mode)
        Returns a short motivational text or meditation script for the break.
        """
        from app.services.model_manager import model_manager
        if not model_manager.is_configured:
            return "Take a deep breath. Hydrate."

        prompt = """
        # MISSION: BREAK TIME COACHING
        **Context:** User just finished a 50m study session.

        **DIRECTIVE:**
        Provide a 30-second reset script.
        - Option A: Box Breathing instruction.
        - Option B: Stoic affirmation.
        - Option C: Physical stretch command.

        **OUTPUT:** Just the text.
        """
        try:
            response = model_manager.generate_content(prompt, model_type='fast')
            return response.text.strip()
        except:
            return "Stand up and stretch."

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
