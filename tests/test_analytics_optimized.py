import sys
import os
import unittest
import json
from unittest.mock import patch, MagicMock

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from app import create_app

class TestAnalyticsOptimized(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True

        # Mock session to be logged in
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1

    @patch('app.routes.analytics.get_all_subjects_performance')
    def test_get_subject_wise_calls_optimized_function(self, mock_get_perf):
        # Test that the route calls the optimized function
        mock_data = [{
            'subject': 'GS1',
            'mock_avg': 50,
            'answer_avg': 60,
            'syllabus_pct': 50.0,
            'pyq_attempted': 0,
            'flashcard_mastered': 0
        }]
        mock_get_perf.return_value = mock_data

        response = self.client.get('/api/analytics/subject-wise')

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['subject'], 'GS1')

        # Verify the service function was called once
        mock_get_perf.assert_called_once()

    def test_get_subject_wise_integration_mock_db(self):
        # We mock get_db in the route, which passes the mock connection to the service
        with patch('app.routes.analytics.get_db') as mock_get_db_route:
             mock_conn = MagicMock()
             mock_get_db_route.return_value = mock_conn

             # The service executes 3 queries.
             # We need to mock the results for them.
             mock_cursor = MagicMock()

             # Mock data needs to match what fetchall returns (list of dict-like)
             # We can use real dicts if row_factory is not used or if code handles dicts
             mock_avgs = [{'subject': 'GS1', 'avg_score': 50}]
             answer_avgs = [{'subject': 'GS1', 'avg_score': 60}]
             syllabus_stats = [{'subject': 'GS1', 'total': 10, 'completed': 5}]

             # fetchall side effects
             mock_cursor.fetchall.side_effect = [mock_avgs, answer_avgs, syllabus_stats]
             mock_conn.execute.return_value = mock_cursor

             response = self.client.get('/api/analytics/subject-wise')

             self.assertEqual(response.status_code, 200)
             data = json.loads(response.data)

             # Find GS1
             gs1 = next((item for item in data if item['subject'] == 'GS1'), None)
             self.assertIsNotNone(gs1)
             self.assertEqual(gs1['mock_avg'], 50)
             self.assertEqual(gs1['answer_avg'], 60)
             self.assertEqual(gs1['syllabus_pct'], 50.0)

if __name__ == '__main__':
    unittest.main()
