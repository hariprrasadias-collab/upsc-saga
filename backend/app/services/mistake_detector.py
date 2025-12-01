from app.db import get_db
from datetime import datetime, timedelta
import json

class MistakeDetector:
    """
    Service to analyze Brain actions and detect patterns of failure or user rejection.
    Uses raw SQLite3 queries.
    """

    def detect_mistakes(self, lookback_hours=24):
        """
        Analyzes action logs from the last N hours to find mistakes.
        Returns a list of detected mistakes.
        """
        conn = get_db()
        
        # Calculate timestamp for lookback
        since = (datetime.utcnow() - timedelta(hours=lookback_hours)).isoformat()
        
        # 1. Fetch failed actions
        failed_actions = conn.execute('''
            SELECT * FROM brain_action_log 
            WHERE executed_at >= ? AND outcome_status = 'failure'
        ''', (since,)).fetchall()

        # 2. Fetch actions with negative impact (User rejected/ignored)
        negative_impact_actions = conn.execute('''
            SELECT * FROM brain_action_log 
            WHERE executed_at >= ? AND impact_score < 0
        ''', (since,)).fetchall()

        mistakes = []

        # Process explicit failures
        for action in failed_actions:
            mistakes.append({
                'type': 'execution_failure',
                'action_id': action['id'],
                'action_type': action['action_type'],
                'reason': 'Action failed to execute successfully.',
                'timestamp': action['executed_at']
            })

        # Process negative impact (rejections)
        for action in negative_impact_actions:
            mistakes.append({
                'type': 'user_rejection',
                'action_id': action['id'],
                'action_type': action['action_type'],
                'reason': 'User ignored or rejected the action (Negative Impact).',
                'timestamp': action['executed_at']
            })

        # 3. Detect Correction Loops (Repeated failures of the same type)
        # Convert Row objects to dicts for easier handling if needed, or just pass list
        all_bad_actions = [dict(row) for row in failed_actions] + [dict(row) for row in negative_impact_actions]
        loop_mistakes = self._detect_loops(all_bad_actions)
        mistakes.extend(loop_mistakes)

        return mistakes

    def _detect_loops(self, bad_actions):
        """
        Identifies if the same action type has failed multiple times recently.
        """
        action_counts = {}
        for action in bad_actions:
            atype = action['action_type']
            if atype not in action_counts:
                action_counts[atype] = []
            action_counts[atype].append(action)

        loops = []
        for action_type, actions in action_counts.items():
            if len(actions) >= 3:  # Threshold for a loop
                loops.append({
                    'type': 'correction_loop',
                    'action_type': action_type,
                    'count': len(actions),
                    'reason': f'Action "{action_type}" has failed or been rejected {len(actions)} times recently.',
                    'action_ids': [a['id'] for a in actions],
                    'timestamp': datetime.utcnow().isoformat()
                })
        
        return loops

    def blacklist_action(self, action_type, reason):
        """
        Temporarily blacklists an action type to prevent further mistakes.
        """
        conn = get_db()
        
        # Check if already blacklisted
        existing = conn.execute('SELECT * FROM brain_action_blacklist WHERE action_type = ?', (action_type,)).fetchone()
        if existing:
            return dict(existing)
        
        expires_at = (datetime.utcnow() + timedelta(hours=24)).isoformat()
        
        cursor = conn.execute('''
            INSERT INTO brain_action_blacklist (action_type, reason, expires_at)
            VALUES (?, ?, ?)
        ''', (action_type, reason, expires_at))
        conn.commit()
        
        return {
            'id': cursor.lastrowid,
            'action_type': action_type,
            'reason': reason,
            'expires_at': expires_at
        }
