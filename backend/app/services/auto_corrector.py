from app.db import get_db
from app.services.brain_service import brain_service
from app.services.autonomy_manager import autonomy_manager
import json
import time

class AutoCorrector:
    """
    Service to automatically correct detected mistakes in Brain actions.
    """

    def correct_mistake(self, mistake):
        """
        Attempt to correct a specific mistake.
        Returns result of correction attempt.
        """
        mistake_type = mistake['type']
        action_type = mistake['action_type']
        
        print(f"🔧 AutoCorrector: Attempting to fix {mistake_type} in {action_type}")

        if mistake_type == 'execution_failure':
            return self._handle_execution_failure(mistake)
        
        elif mistake_type == 'user_rejection':
            return self._handle_user_rejection(mistake)
        
        elif mistake_type == 'correction_loop':
            return self._handle_correction_loop(mistake)
            
        return {'success': False, 'message': 'Unknown mistake type'}

    def _handle_execution_failure(self, mistake):
        """
        Strategy: Retry with backoff or simplified parameters.
        """
        # Simple retry for now
        # In a real system, we'd check the error message to decide strategy
        
        # Fetch original action payload
        conn = get_db()
        action = conn.execute('SELECT * FROM brain_action_log WHERE id = ?', (mistake['action_id'],)).fetchone()
        
        if not action:
            return {'success': False, 'message': 'Original action not found'}
            
        payload = json.loads(action['action_payload']) if action['action_payload'] else {}
        
        # Retry logic
        print(f"🔄 Retrying {action['action_type']}...")
        
        # Log the correction attempt
        autonomy_manager.log_action(
            action_type=f"RETRY_{action['action_type']}",
            action_payload=payload,
            executed_by='auto_corrector',
            reasoning=f"Retrying after failure: {mistake['reason']}"
        )
        
        # Execute via BrainService
        result = brain_service.execute_action(action['action_type'], payload)
        
        return {
            'success': result['success'],
            'message': f"Retry result: {result['message']}",
            'new_action_id': result.get('action_id')
        }

    def _handle_user_rejection(self, mistake):
        """
        Strategy: Adjust parameters (e.g., lower intensity) or try alternative.
        """
        conn = get_db()
        action = conn.execute('SELECT * FROM brain_action_log WHERE id = ?', (mistake['action_id'],)).fetchone()
        
        if not action:
            return {'success': False, 'message': 'Original action not found'}
            
        payload = json.loads(action['action_payload']) if action['action_payload'] else {}
        action_type = action['action_type']
        
        new_payload = payload.copy()
        correction_strategy = "None"
        
        # Parameter Adjustment Logic
        if action_type == 'CREATE_FLASHCARDS':
            # If user ignored 20 cards, try 5
            count = payload.get('count', 10)
            if count > 5:
                new_payload['count'] = 5
                correction_strategy = "Reduced flashcard count"
            else:
                return {'success': False, 'message': 'Cannot reduce parameters further. Blacklisting temporarily.'}
                
        elif action_type == 'SCHEDULE_REVISION':
            # If user ignored revision, maybe try a different topic or shorter duration
            # For now, let's just log it as unfixable without more complex logic
            return {'success': False, 'message': 'Complex rejection - requires manual strategy change.'}
            
        else:
            return {'success': False, 'message': f'No auto-correction strategy for {action_type} rejection.'}
            
        # Execute adjusted action
        print(f"📉 Adjusting {action_type}: {correction_strategy}")
        
        autonomy_manager.log_action(
            action_type=f"ADJUSTED_{action_type}",
            action_payload=new_payload,
            executed_by='auto_corrector',
            reasoning=f"User rejected previous attempt. Strategy: {correction_strategy}"
        )
        
        result = brain_service.execute_action(action_type, new_payload)
        
        return {
            'success': result['success'],
            'message': f"Correction ({correction_strategy}) result: {result['message']}",
            'new_action_id': result.get('action_id')
        }

    def _handle_correction_loop(self, mistake):
        """
        Strategy: Blacklist the action type temporarily to stop the loop.
        """
        from app.services.mistake_detector import MistakeDetector
        detector = MistakeDetector()
        
        entry = detector.blacklist_action(
            mistake['action_type'], 
            reason=f"Auto-detected correction loop: {mistake['reason']}"
        )
        
        return {
            'success': True,
            'message': f"Loop detected. Action {mistake['action_type']} blacklisted until {entry['expires_at']}"
        }

# Singleton instance
auto_corrector = AutoCorrector()
