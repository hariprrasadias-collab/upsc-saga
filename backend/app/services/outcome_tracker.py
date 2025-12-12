"""
Outcome Tracker - Measures effectiveness of Brain's actions
Learns from successes and failures to improve future decisions
"""
from app.db import get_db
import json
from datetime import datetime, timedelta

class OutcomeTracker:
    """Tracks and measures the impact of Brain's autonomous actions"""
    
    @staticmethod
    def measure_action_impact(action_id):
        """
        Measure the impact of an action 24-48 hours after execution.
        Returns impact score from -1.0 (harmful) to 1.0 (very helpful)
        """
        conn = get_db()
        
        # Get the action details
        action = conn.execute(
            'SELECT * FROM brain_action_log WHERE id = ?',
            (action_id,)
        ).fetchone()
        
        if not action:
            return None
        
        action_type = action['action_type']
        payload = json.loads(action['action_payload']) if action['action_payload'] else {}
        executed_at = datetime.fromisoformat(action['executed_at'])
        
        impact_score = 0.0
        
        # Measure based on action type
        if action_type == 'CREATE_FLASHCARDS':
            impact_score = OutcomeTracker._measure_flashcard_creation(payload, executed_at)
        
        elif action_type == 'CREATE_MOCK_TEST':
            impact_score = OutcomeTracker._measure_mock_test_creation(payload, executed_at)
        
        elif action_type == 'SCHEDULE_REVISION':
            impact_score = OutcomeTracker._measure_revision_scheduling(payload, executed_at)
        
        elif action_type == 'CURATE_CONTENT':
            impact_score = OutcomeTracker._measure_content_curation(payload, executed_at)
        
        elif action_type == 'TRIGGER_RETENTION_LOCKDOWN':
            impact_score = OutcomeTracker._measure_retention_lockdown(payload, executed_at)
        
        # Update the action log with the impact score
        conn.execute('''
            UPDATE brain_action_log
            SET impact_score = ?,
                outcome_measured_at = CURRENT_TIMESTAMP,
                outcome_status = CASE
                    WHEN ? > 0.5 THEN 'success'
                    WHEN ? < -0.3 THEN 'failure'
                    ELSE 'neutral'
                END
            WHERE id = ?
        ''', (impact_score, impact_score, impact_score, action_id))
        conn.commit()
        
        # Learn from this outcome
        OutcomeTracker._learn_from_outcome(action, impact_score)
        
        return impact_score
    
    @staticmethod
    def _measure_flashcard_creation(payload, executed_at):
        """Did the user actually review the flashcards we created?"""
        conn = get_db()
        
        # Get deck_id from payload
        topic = payload.get('topic', '')
        
        # Count how many flashcards were reviewed since creation
        reviews = conn.execute('''
            SELECT COUNT(DISTINCT rs.flashcard_id) as reviewed_count
            FROM review_sessions rs
            JOIN flashcards f ON rs.flashcard_id = f.id
            WHERE rs.reviewed_at > ?
            AND rs.reviewed_at < ?
        ''', (executed_at, executed_at + timedelta(hours=48))).fetchone()
        
        reviewed_count = reviews['reviewed_count'] if reviews else 0
        card_count = payload.get('count', 5)
        
        if reviewed_count == 0:
            return -0.7  # User ignored them completely
        elif reviewed_count >= card_count * 0.8:
            return 1.0  # Great engagement!
        elif reviewed_count >= card_count * 0.5:
            return 0.6  # Decent engagement
        else:
            return 0.2  # Partial engagement
    
    @staticmethod
    def _measure_mock_test_creation(payload, executed_at):
        """Did the user take the mock test?"""
        conn = get_db()
        
        # Check if any mock test was completed within 48 hours
        tests = conn.execute('''
            SELECT COUNT(*) as count
            FROM test_attempts
            WHERE user_id = 1
            AND submitted_at > ?
            AND submitted_at < ?
            AND status = 'completed'
        ''', (executed_at, executed_at + timedelta(hours=72))).fetchone()
        
        if tests and tests['count'] > 0:
            return 0.9  # Success - user took a test
        else:
            return -0.5  # User didn't take it
    
    @staticmethod
    def _measure_revision_scheduling(payload, executed_at):
        """Did the user actually study the scheduled topics?"""
        conn = get_db()
        
        # Check for Pomodoro sessions or study activity
        sessions = conn.execute('''
            SELECT COUNT(*) as count
            FROM pomodoro_sessions
            WHERE user_id = 1
            AND started_at > ?
            AND started_at < ?
            AND status = 'completed'
        ''', (executed_at, executed_at + timedelta(days=2))).fetchone()
        
        if sessions and sessions['count'] >= 2:
            return 0.8  # Good follow-through
        elif sessions and sessions['count'] == 1:
            return 0.4  # Some follow-through
        else:
            return -0.3  # No follow-through
    
    @staticmethod
    def _measure_content_curation(payload, executed_at):
        """Did the user engage with curated content?"""
        # This is harder to measure without click tracking
        # For now, assume moderate success if action was taken
        return 0.5  # Neutral - can't measure clicks yet
    
    @staticmethod
    def _measure_retention_lockdown(payload, executed_at):
        """Did the lockdown help clear the backlog?"""
        conn = get_db()
        
        # Check if due card count decreased
        initial_due = payload.get('due_count', 0)
        
        # Count current due cards
        current_due = conn.execute('''
            SELECT COUNT(*) as count
            FROM flashcards f
            JOIN review_sessions rs ON f.id = rs.flashcard_id
            WHERE rs.next_review < CURRENT_TIMESTAMP
        ''').fetchone()
        
        current_count = current_due['count'] if current_due else 0
        reduction = initial_due - current_count
        
        if reduction >= initial_due * 0.5:
            return 1.0  # Major improvement!
        elif reduction >= initial_due * 0.25:
            return 0.6  # Good progress
        elif reduction > 0:
            return 0.3  # Some progress
        else:
            return -0.2  # No improvement
    
    @staticmethod
    def _learn_from_outcome(action, impact_score):
        """Extract patterns from action outcomes and store for learning"""
        conn = get_db()
        
        context = json.loads(action['context_snapshot']) if action['context_snapshot'] else {}
        
        if impact_score > 0.7:
            # Successful action - store pattern
            pattern_data = {
                'action_type': action['action_type'],
                'payload': json.loads(action['action_payload']) if action['action_payload'] else {},
                'context': {
                    'hour_of_day': context.get('hour_of_day'),
                    'day_of_week': context.get('day_of_week')
                },
                'impact_score': impact_score
            }
            
            OutcomeTracker._store_pattern('successful_workflow', pattern_data, confidence=impact_score)
        
        elif impact_score < -0.3:
            # Failed action - remember to avoid
            pattern_data = {
                'action_type': action['action_type'],
                'failure_reason': 'User did not engage',
                'context': context
            }
            
            OutcomeTracker._store_pattern('failed_action', pattern_data, confidence=abs(impact_score))
    
    @staticmethod
    def _store_pattern(pattern_type, pattern_data, confidence=0.5):
        """Store or update a learned pattern"""
        conn = get_db()
        
        # Check if similar pattern exists
        pattern_json = json.dumps(pattern_data, sort_keys=True)
        
        existing = conn.execute('''
            SELECT id, times_observed, confidence_score
            FROM brain_learning_patterns
            WHERE pattern_type = ?
            AND pattern_data = ?
        ''', (pattern_type, pattern_json)).fetchone()
        
        if existing:
            # Update existing pattern
            new_observations = existing['times_observed'] + 1
            # Increase confidence with each observation (max 1.0)
            new_confidence = min(1.0, existing['confidence_score'] + 0.05)
            
            conn.execute('''
                UPDATE brain_learning_patterns
                SET times_observed = ?,
                    confidence_score = ?,
                    last_observed = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (new_observations, new_confidence, existing['id']))
        else:
            # Create new pattern
            conn.execute('''
                INSERT INTO brain_learning_patterns
                (user_id, pattern_type, pattern_data, confidence_score, times_observed)
                VALUES (1, ?, ?, ?, 1)
            ''', (pattern_type, pattern_json, confidence))
        
        conn.commit()
    
    @staticmethod
    def get_learned_patterns(pattern_type=None, min_confidence=0.5):
        """Retrieve learned patterns for decision-making"""
        conn = get_db()
        
        if pattern_type:
            patterns = conn.execute('''
                SELECT * FROM brain_learning_patterns
                WHERE pattern_type = ?
                AND confidence_score >= ?
                ORDER BY confidence_score DESC, times_observed DESC
            ''', (pattern_type, min_confidence)).fetchall()
        else:
            patterns = conn.execute('''
                SELECT * FROM brain_learning_patterns
                WHERE confidence_score >= ?
                ORDER BY confidence_score DESC, times_observed DESC
            ''', (min_confidence,)).fetchall()
        
        return [
            {
                'id': p['id'],
                'type': p['pattern_type'],
                'data': json.loads(p['pattern_data']),
                'confidence': p['confidence_score'],
                'observations': p['times_observed']
            }
            for p in patterns
        ]
    
    @staticmethod
    def should_suggest_action(action_type, current_context):
        """
        Use learned patterns to decide if an action should be suggested.
        Returns (should_suggest: bool, confidence: float, reasoning: str)
        """
        conn = get_db()
        
        # Check if action is blacklisted
        blacklisted = conn.execute('''
            SELECT COUNT(*) as count FROM brain_action_blacklist
            WHERE action_type = ?
            AND (blacklist_until IS NULL OR blacklist_until > CURRENT_TIMESTAMP)
        ''', (action_type,)).fetchone()
        
        if blacklisted and blacklisted['count'] > 0:
            return (False, 0.0, "Action is blacklisted due to repeated failures")
        
        # Check successful patterns
        successful_patterns = OutcomeTracker.get_learned_patterns('successful_workflow', min_confidence=0.6)
        matching_successes = [p for p in successful_patterns if p['data']['action_type'] == action_type]
        
        # Check failed patterns
        failed_patterns = OutcomeTracker.get_learned_patterns('failed_action', min_confidence=0.5)
        matching_failures = [p for p in failed_patterns if p['data']['action_type'] == action_type]
        
        if matching_successes and not matching_failures:
            avg_confidence = sum(p['confidence'] for p in matching_successes) / len(matching_successes)
            return (True, avg_confidence, f"Learned from {len(matching_successes)} successful occurrences")
        
        elif matching_failures and not matching_successes:
            return (False, 0.0, f"Previously failed {len(matching_failures)} times")
        
        elif matching_successes and matching_failures:
            success_score = sum(p['confidence'] for p in matching_successes) / len(matching_successes)
            failure_score = sum(p['confidence'] for p in matching_failures) / len(matching_failures)
            
            if success_score > failure_score:
                return (True, success_score - failure_score, "More successes than failures")
            else:
                return (False, 0.0, "More failures than successes")
        
        # No patterns yet - neutral
        return (True, 0.5, "No prior data - suggesting with caution")

    @staticmethod
    def analyze_prediction_accuracy(prediction_id, actual_outcome):
        """
        PHASE 16: THE POST-MORTEM
        Analyzes why a Foresight prediction was right or wrong.
        """
        from app.services.model_manager import model_manager
        if not model_manager.is_configured:
            return "Analysis Unavailable"

        prompt = f"""
        # MISSION: PREDICTION POST-MORTEM
        **Prediction ID:** {prediction_id}
        **Actual Outcome:** {actual_outcome}

        **DIRECTIVE:**
        Analyze the gap. Did the AI miss a variable? Was it a Black Swan?

        **OUTPUT:**
        A 1-sentence analytical verdict.
        """
        try:
            response = model_manager.generate_content(prompt, model_type='pro')
            return response.text.strip()
        except:
            return "Analysis Failed."

# Singleton instance
outcome_tracker = OutcomeTracker()
