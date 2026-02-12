import unittest
from unittest.mock import MagicMock, patch
from flask import Flask, session
import sys
import os
import json
from datetime import date, timedelta

# Ensure backend is in path so we can import app modules
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

# Import the blueprint
from app.routes.analytics import analytics

class TestAnalyticsOptimized(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.secret_key = 'test_secret'
        # Register blueprint
        self.app.register_blueprint(analytics)
        self.client = self.app.test_client()

    @patch('app.routes.analytics.get_db')
    def test_progress_trend_optimization(self, mock_get_db):
        """
        Verifies that get_progress_trend uses optimized queries
        and correctly reconstructs historical data.
        """
        # Mock DB connection
        mock_conn = MagicMock()
        mock_get_db.return_value = mock_conn

        # Mock Data Setup
        today = date.today()
        start_date = today - timedelta(days=30)

        # Scenario:
        # Total topics: 100
        # Completed:
        # - 10 completed on (today - 40 days) -> BEFORE start_date
        # - 5 completed on (today - 10 days) -> INSIDE range
        # - 5 completed on (today - 5 days) -> INSIDE range
        # Total completed today should be 20.

        # We expect the API to return a trend starting at 10% (10/100)
        # and rising to 15% (15/100) then 20% (20/100).

        day_before = (today - timedelta(days=40)).isoformat()
        day_inside1 = (today - timedelta(days=10)).isoformat()
        day_inside2 = (today - timedelta(days=5)).isoformat()

        # Mock execute behavior based on query content
        def execute_side_effect(query, args=()):
            query_upper = query.strip().upper()

            # 1. Total Count Query
            if 'SELECT COUNT(*) FROM SYLLABUS_TOPICS' in query_upper and 'WHERE' not in query_upper:
                m = MagicMock()
                # Simulate fetchone()[0] returning 100
                m.fetchone.return_value = [100]
                return m

            # 2. Optimized Aggregation Query
            elif 'GROUP BY DATE(LAST_UPDATED)' in query_upper:
                m = MagicMock()
                # Simulate fetchall() returning list of rows (dicts)
                # Note: The code handles rows as dicts via sqlite3.Row usually
                m.fetchall.return_value = [
                    {'date': day_before, 'count': 10},
                    {'date': day_inside1, 'count': 5},
                    {'date': day_inside2, 'count': 5}
                ]
                return m

            # 3. Old Inefficient Query (Fallback / Check for regression)
            elif 'SELECT COUNT(*) FROM SYLLABUS_TOPICS' in query_upper and 'WHERE STATUS' in query_upper:
                # If this is called, it means the optimization wasn't applied or logic is mixed.
                # We return a static value (e.g. 20) to simulate the "flat line" behavior if loop persists.
                m = MagicMock()
                m.fetchone.return_value = [20]
                return m

            # Default empty result
            m = MagicMock()
            m.fetchone.return_value = None
            m.fetchall.return_value = []
            return m

        mock_conn.execute.side_effect = execute_side_effect

        # Simulate logged in user
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1

        # Call API
        response = self.client.get('/api/analytics/progress-trend?metric=syllabus&days=30')
        data = response.get_json()

        # Verification
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(data) > 0, "Response data should not be empty")

        # Check start value (should include pre-range completions)
        # 10 completed before range / 100 total = 10%
        # The first point corresponds to start_date.
        # Since day_before < start_date, it should be counted.
        first_point = data[0]
        self.assertEqual(first_point['value'], 10.0, f"Expected 10.0% at start, got {first_point['value']}%")

        # Check end value (should include all completions)
        # 20 completed total / 100 total = 20%
        last_point = data[-1]
        self.assertEqual(last_point['value'], 20.0, f"Expected 20.0% at end, got {last_point['value']}%")

        # Check intermediate value
        # Find the date corresponding to day_inside1
        # day_inside1 is -10 days.
        # The list has 31 points (0 to 30).
        # We can iterate to check the jump.

        prev_val = 10.0
        jumps = 0
        for point in data:
            if point['value'] > prev_val:
                jumps += 1
                prev_val = point['value']

        # We expect 2 jumps (from 10 to 15, then 15 to 20)
        # Note: If multiple days fall on same date, it's one jump. Here dates differ.
        self.assertEqual(jumps, 2, f"Expected 2 jumps in progress, found {jumps}")

        # Check Call Count
        # If optimized, we expect roughly 2 calls (Total + Group By).
        # If unoptimized, we expect ~62 calls (2 * 31).
        # We allow small margin but clearly < 10.
        call_count = mock_conn.execute.call_count
        self.assertTrue(call_count < 10, f"Too many DB calls: {call_count}. Expected optimization.")

if __name__ == '__main__':
    unittest.main()
