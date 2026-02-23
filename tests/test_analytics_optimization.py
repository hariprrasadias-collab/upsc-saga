import unittest
from unittest.mock import MagicMock, patch
from flask import Flask, session
import sys
import os

# Ensure backend is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

# We need to import the blueprint after setting up the path
# But we also need to mock get_db BEFORE it's imported if it's imported at module level
# However, analytics.py imports get_db inside the function (no, at top level)
# `from app.db import get_db` at top level.
# So we need to patch where it is USED, which is `app.routes.analytics.get_db`.

from app.routes.analytics import analytics

class TestAnalyticsOptimization(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.register_blueprint(analytics)
        self.app.secret_key = 'test'
        self.client = self.app.test_client()

    @patch('app.routes.analytics.get_db')
    def test_get_progress_trend_optimization(self, mock_get_db):
        # Mock DB connection
        mock_conn = MagicMock()
        mock_get_db.return_value = mock_conn

        # Setup mock return values for execute().fetchone()
        # The code calls:
        # 1. count completed
        # 2. count total

        # Simulate execute().fetchone()[0] returning 50 then 100 repeatedly
        # To make it robust, let's use side_effect on the cursor
        mock_cursor = MagicMock()
        mock_conn.execute.return_value = mock_cursor

        # We need to handle the two different queries.
        # Query 1: ... WHERE status = 'Completed' ...
        # Query 2: ... FROM syllabus_topics ... (total)

        def execute_side_effect(query, args=()):
            cursor = MagicMock()
            if "status = 'Completed'" in query:
                cursor.fetchone.return_value = [50]
            elif "FROM syllabus_topics" in query:
                cursor.fetchone.return_value = [100]
            else:
                cursor.fetchone.return_value = [0]
            return cursor

        mock_conn.execute.side_effect = execute_side_effect

        # Mock session
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1

        days = 5
        response = self.client.get(f'/api/analytics/progress-trend?metric=syllabus&days={days}')

        self.assertEqual(response.status_code, 200)
        data = response.json

        # Check structure
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), days + 1) # 0 to 5 days = 6 points

        # Check values
        for point in data:
            self.assertEqual(point['value'], 50.0) # 50/100 * 100 = 50.0

        # Count calls to execute
        # Unoptimized: 2 calls per day * (days + 1)
        # Optimized: 2 calls total.

        call_count = mock_conn.execute.call_count
        print(f"\n[Test Output] DB Execute called {call_count} times for {days + 1} data points.")

        if call_count > 2:
            print("[Test Output] Behavior: Unoptimized (N+1 queries detected)")
        else:
            print("[Test Output] Behavior: Optimized (Constant queries)")

if __name__ == '__main__':
    unittest.main()
