"""
Autonomy Manager - Controls Brain's autonomous execution capabilities
"""
from app.db import get_db
import json

class AutonomyManager:
    """Manages autonomy levels and auto-execution permissions"""
    
    AUTONOMY_LEVELS = {
        'manual': {
            'description': 'Brain suggests actions, user approves all',
            'auto_execute': []
        },
        'semi_auto': {
            'description': 'Brain auto-executes low-risk actions only',
            'auto_execute': ['CURATE_CONTENT', 'SCHEDULE_REVISION']
        },
        'full_auto': {
            'description': 'Brain operates independently with oversight',
            'auto_execute': ['*']  # All actions except DELETE operations
        }
    }
    
    SAFE_AUTO_ACTIONS = [
        'CURATE_CONTENT',
        'SCHEDULE_REVISION',
        'CREATE_FLASHCARDS',  # Can be undone
        'CREATE_MOCK_TEST'     # Can be undone
    ]
    
    RESTRICTED_ACTIONS = [
        'DELETE_FLASHCARDS',
        'DELETE_DECK',
        'RESET_PROGRESS'
    ]
    
    @staticmethod
    def get_user_autonomy_level(user_id=1):
        """Get user's current autonomy preference"""
        conn = get_db()
        result = conn.execute(
            'SELECT autonomy_level FROM brain_user_preferences WHERE user_id = ?',
            (user_id,)
        ).fetchone()
        
        return result['autonomy_level'] if result else 'manual'
    
    @staticmethod
    def set_user_autonomy_level(user_id, level):
        """Update user's autonomy level"""
        if level not in AutonomyManager.AUTONOMY_LEVELS:
            raise ValueError(f"Invalid autonomy level: {level}")
        
        conn = get_db()
        conn.execute('''
            INSERT INTO brain_user_preferences (user_id, autonomy_level, last_updated)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                autonomy_level = excluded.autonomy_level,
                last_updated = CURRENT_TIMESTAMP
        ''', (user_id, level))
        conn.commit()
    
    @staticmethod
    def can_auto_execute(action_type, user_id=1):
        """Check if action can be auto-executed based on user's autonomy level"""
        
        # Never auto-execute restricted actions
        if action_type in AutonomyManager.RESTRICTED_ACTIONS:
            return False
        
        autonomy_level = AutonomyManager.get_user_autonomy_level(user_id)
        allowed_actions = AutonomyManager.AUTONOMY_LEVELS[autonomy_level]['auto_execute']
        
        # Full auto mode
        if '*' in allowed_actions:
            return action_type in AutonomyManager.SAFE_AUTO_ACTIONS
        
        # Specific actions allowed
        return action_type in allowed_actions
    
    @staticmethod
    def is_action_blacklisted(action_type):
        """Check if action is temporarily blacklisted due to repeated failures"""
        conn = get_db()
        result = conn.execute('''
            SELECT COUNT(*) as count FROM brain_action_blacklist
            WHERE action_type = ?
            AND (blacklist_until IS NULL OR blacklist_until > CURRENT_TIMESTAMP)
        ''', (action_type,)).fetchone()
        
        return result['count'] > 0
    
    @staticmethod
    def log_action(action_type, action_payload, executed_by='manual', 
                   reasoning=None, confidence_score=1.0, user_id=1):
        """Log a Brain action for tracking and learning"""
        conn = get_db()
        
        # Get current system context
        context_snapshot = AutonomyManager._get_context_snapshot()
        
        cursor = conn.execute('''
            INSERT INTO brain_action_log (
                user_id, action_type, action_payload, action_label,
                executed_by, reasoning, confidence_score, context_snapshot
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            action_type,
            json.dumps(action_payload),
            action_payload.get('label', action_type),
            executed_by,
            reasoning,
            confidence_score,
            json.dumps(context_snapshot)
        ))
        conn.commit()
        
        return cursor.lastrowid
    
    @staticmethod
    def update_action_outcome(action_id, outcome_status, impact_score=None, 
                             user_feedback=None):
        """Update the outcome of a logged action"""
        conn = get_db()
        conn.execute('''
            UPDATE brain_action_log
            SET outcome_status = ?,
                outcome_measured_at = CURRENT_TIMESTAMP,
                impact_score = COALESCE(?, impact_score),
                user_feedback = COALESCE(?, user_feedback)
            WHERE id = ?
        ''', (outcome_status, impact_score, user_feedback, action_id))
        conn.commit()
    
    @staticmethod
    def _get_context_snapshot():
        """Capture current system state for learning"""
        from app.services.brain_service import brain_service
        from datetime import datetime
        
        try:
            # Get basic context
            status = brain_service._get_system_status_summary()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'hour_of_day': datetime.now().hour,
                'day_of_week': datetime.now().weekday(),
                'system_status': status
            }
        except Exception as e:
            print(f"Error getting context snapshot: {e}")
            return {'timestamp': datetime.now().isoformat()}
    
    @staticmethod
    def get_autonomy_stats(user_id=1):
        """Get statistics about autonomous operations"""
        conn = get_db()
        
        # Total actions
        total = conn.execute(
            'SELECT COUNT(*) as count FROM brain_action_log WHERE user_id = ?',
            (user_id,)
        ).fetchone()
        
        # Auto-executed actions
        auto_executed = conn.execute(
            'SELECT COUNT(*) as count FROM brain_action_log WHERE user_id = ? AND executed_by = "auto"',
            (user_id,)
        ).fetchone()
        
        # Success rate
        success = conn.execute(
            'SELECT AVG(impact_score) as avg FROM brain_action_log WHERE user_id = ? AND impact_score IS NOT NULL',
            (user_id,)
        ).fetchone()
        
        return {
            'total_actions': total['count'],
            'auto_executed_count': auto_executed['count'],
            'auto_execution_rate': auto_executed['count'] / total['count'] if total['count'] > 0 else 0,
            'average_success_score': success['avg'] if success and success['avg'] else 0
        }

# Singleton instance
autonomy_manager = AutonomyManager()
