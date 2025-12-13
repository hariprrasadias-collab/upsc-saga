import json
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Mock Flask and DB
class MockCursor:
    def __init__(self, data=None):
        self.data = data or []
        self.lastrowid = 1

    def execute(self, query, params=None):
        return self

    def fetchone(self):
        if self.data:
            return self.data[0]
        return None

    def fetchall(self):
        return self.data

class MockConn:
    def execute(self, query, params=None):
        # Return generic data for various queries
        if "SELECT * FROM brain_action_log WHERE id = ?" in query:
             return MockCursor([{'id': 1, 'action_type': 'TEST_ACTION', 'action_payload': '{"key": "value"}'}])

        # SelfReview stats
        if "COUNT(*) as total_actions" in query:
             return MockCursor([{'total_actions': 10, 'successes': 8, 'failures': 2, 'avg_impact': 0.8}])

        if "outcome_status = 'failure'" in query:
             return MockCursor([{'action_type': 'FAIL_ACTION', 'count': 2}])

        if "outcome_status = 'success'" in query:
             return MockCursor([{'action_type': 'SUCCESS_ACTION', 'count': 8}])

        if "brain_self_reviews" in query:
             return MockCursor([{'review_week': '2023-W01', 'improvement_plan': '["Plan A"]'}])

        return MockCursor()

    def commit(self):
        pass

    def cursor(self):
        return MockCursor()

    def close(self):
        pass

# Mock DB Getter
def mock_get_db():
    return MockConn()

# Mock BrainService
class MockBrainService:
    def execute_action(self, action_type, payload):
        return {'success': True, 'message': 'Mock Execution Success', 'action_id': 99}

# Mock ModelManager
class MockModelManager:
    def __init__(self):
        self.is_configured = True

    def generate_content(self, prompt, model_type='fast'):
        mock_response = MagicMock()
        mock_response.text = '{"plan": ["Mock Improvement 1", "Mock Improvement 2"]}'
        if "Auto-Correct" in prompt:
             mock_response.text = '{"key": "corrected_value"}'
        if "You are a UPSC expert analyzer" in prompt:
             mock_response.text = '{"upsc_summary": "Summary", "key_points": ["Point 1"], "papers": ["GS3"], "subjects": ["Economics"], "importance": 3}'
        return mock_response

# Patch imports globally before importing modules
sys.modules['app.db'] = MagicMock()
sys.modules['app.db'].get_db = mock_get_db
sys.modules['app.services.brain_service'] = MagicMock()
sys.modules['app.services.brain_service'].brain_service = MockBrainService()
sys.modules['app.services.model_manager'] = MagicMock()
sys.modules['app.services.model_manager'].model_manager = MockModelManager()
sys.modules['app.services.autonomy_manager'] = MagicMock()

# Import services to test
from app.services.auto_corrector import AutoCorrector
from app.services.self_review import SelfReviewService
from app.services.upsc_summarizer import summarize_for_upsc

class TestFinalPhase(unittest.TestCase):

    def test_auto_corrector_retry(self):
        print("\nTesting AutoCorrector Retry Logic...")
        corrector = AutoCorrector()
        mistake = {'action_id': 1, 'reason': 'Context Window Exceeded'}

        result = corrector._handle_execution_failure(mistake)
        print(f"Result: {result}")

        self.assertTrue(result['success'])
        self.assertIn('AI Adjusted Payload', result['message'])

    def test_self_review_plan(self):
        print("\nTesting SelfReview AI Plan Generation...")
        service = SelfReviewService()

        # Test perform_review
        result = service.perform_review(lookback_days=7)
        print(f"Result: {result}")

        self.assertIn('improvement_plan', result)
        self.assertIsInstance(result['improvement_plan'], dict)
        self.assertIn('plan', result['improvement_plan'])

    def test_upsc_summarizer(self):
        print("\nTesting UPSCSummarizer ModelManager Integration...")
        result = summarize_for_upsc("Test Title", "Test Content Economics", "http://test.com")
        print(f"Result: {result}")

        self.assertEqual(result['papers'], ['GS3'])
        self.assertEqual(result['subjects'], ['Economics'])

if __name__ == '__main__':
    unittest.main()
