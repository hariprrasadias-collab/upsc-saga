import os
import unittest
import sqlite3
import tempfile
import json
from datetime import datetime, timedelta
import sys
from unittest.mock import patch

# Ensure we can import app
sys.path.append(os.getcwd())
if 'backend' not in os.getcwd():
     sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Import app modules normally
try:
    from app import create_app
    from app.db import get_db
    import app.db as db_module # Import the module to patch
except ImportError:
    sys.path.append(os.path.join(os.getcwd(), 'backend'))
    from app import create_app
    from app.db import get_db
    import app.db as db_module

class AnalyticsPerfTest(unittest.TestCase):
    def setUp(self):
        # Create temp file for DB
        self.db_fd, self.db_path = tempfile.mkstemp()

        # Patch the DATABASE global in app.db
        self.patcher = patch('app.db.DATABASE', self.db_path)
        self.patcher.start()

        self.app = create_app()
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()

        # Verify we are using the temp DB
        self.conn = get_db()

        # Manually create table since create_app doesn't call init_syllabus_tables
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS syllabus_topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                topic TEXT NOT NULL,
                sub_topic TEXT,
                status TEXT DEFAULT 'Not Started',
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Ensure we start with a clean state for syllabus_topics
        self.conn.execute("DELETE FROM syllabus_topics")
        self.conn.commit()

        self.populate_data()

        # Mock session
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1

    def tearDown(self):
        self.ctx.pop()
        self.patcher.stop()
        os.close(self.db_fd)
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def populate_data(self):
        # Insert test data
        today = datetime.now()

        # 10 topics completed 40 days ago
        date_40_days_ago = (today - timedelta(days=40)).strftime('%Y-%m-%d %H:%M:%S')
        for i in range(10):
            self.conn.execute("INSERT INTO syllabus_topics (subject, topic, status, last_updated) VALUES ('Test', 'Topic', 'Completed', ?)", (date_40_days_ago,))

        # 5 topics completed 20 days ago
        date_20_days_ago = (today - timedelta(days=20)).strftime('%Y-%m-%d %H:%M:%S')
        for i in range(5):
            self.conn.execute("INSERT INTO syllabus_topics (subject, topic, status, last_updated) VALUES ('Test', 'Topic', 'Completed', ?)", (date_20_days_ago,))

        # 5 topics completed 5 days ago
        date_5_days_ago = (today - timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S')
        for i in range(5):
            self.conn.execute("INSERT INTO syllabus_topics (subject, topic, status, last_updated) VALUES ('Test', 'Topic', 'Completed', ?)", (date_5_days_ago,))

        # 20 topics not started (last_updated doesn't matter much but let's say recent)
        for i in range(20):
            self.conn.execute("INSERT INTO syllabus_topics (subject, topic, status, last_updated) VALUES ('Test', 'Topic', 'Not Started', ?)", (today.strftime('%Y-%m-%d %H:%M:%S'),))

        self.conn.commit()

        # Total topics = 40. Completed = 20.
        # Current completion = 20/40 = 50%.

    def test_get_progress_trend(self):
        print("\n--- Testing Progress Trend ---")
        response = self.client.get('/api/analytics/progress-trend?metric=syllabus&days=30')
        data = response.get_json()

        self.assertEqual(len(data), 31) # 30 days + today

        first_day = data[0]
        last_day = data[-1]

        print(f"First day value (30 days ago): {first_day['value']}")
        print(f"Last day value (Today): {last_day['value']}")

        # Logic verification
        # Expected behavior (Fixed):
        # - Day 0 (-30 days): 10 topics completed (-40 days) / 40 total = 25.0%
        # - Day 30 (Today): 10 + 5 (-20 days) + 5 (-5 days) = 20 topics / 40 total = 50.0%

        self.assertEqual(first_day['value'], 25.0, "Progress should start at 25.0% (historical)")
        self.assertEqual(last_day['value'], 50.0, "Progress should end at 50.0% (current)")

        # Check inflection point at -20 days (index 10)
        # At index 10 (today - 20 days), the 5 topics completed on that day should count
        # Wait, if completion is AT -20 days, it counts for that day.
        # index 0 = -30, index 10 = -20.

        mid_day = data[10] # -20 days
        print(f"Mid day value (-20 days): {mid_day['value']}")
        self.assertEqual(mid_day['value'], 37.5, "Progress should be 37.5% at -20 days")

        return data

if __name__ == '__main__':
    unittest.main()
