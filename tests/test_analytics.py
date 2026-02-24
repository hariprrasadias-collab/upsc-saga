
import unittest
import os
import sqlite3
import json

# Set environment variable BEFORE importing app
os.environ['DATABASE_PATH'] = 'test_upsc_saga.db'

from app import create_app
from app.db import get_db

class AnalyticsTestCase(unittest.TestCase):
    def setUp(self):
        self.db_path = 'test_upsc_saga.db'
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        # Initialize database
        with self.app.app_context():
            self._init_db()

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def _init_db(self):
        # create necessary tables for the test
        conn = get_db()
        conn.execute('''
            CREATE TABLE IF NOT EXISTS syllabus_topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paper TEXT NOT NULL,
                subject TEXT NOT NULL,
                topic TEXT NOT NULL,
                subtopic TEXT,
                status TEXT DEFAULT 'Not Started',
                notes TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        # Clear existing data if any (in case reuse happens)
        conn.execute("DELETE FROM syllabus_topics")

        # Insert sample data
        for i in range(50):
            conn.execute("INSERT INTO syllabus_topics (paper, subject, topic, status) VALUES ('GS1', 'History', ?, 'Completed')", (f'Topic {i}',))
        for i in range(50):
            conn.execute("INSERT INTO syllabus_topics (paper, subject, topic, status) VALUES ('GS1', 'History', ?, 'Not Started')", (f'Topic {i+50}',))
        conn.commit()

    def test_get_progress_trend_syllabus(self):
        with self.app.app_context(): # Ensure we have app context
            response = self.client.get('/api/analytics/progress-trend?metric=syllabus&days=30')
            self.assertEqual(response.status_code, 200)
            data = response.json
            self.assertTrue(isinstance(data, list))
            self.assertEqual(len(data), 31) # 30 days + today

            # Check values
            # 50 completed out of 100 total = 50%
            first_entry = data[0]
            self.assertEqual(first_entry['value'], 50.0)

            last_entry = data[-1]
            self.assertEqual(last_entry['value'], 50.0)

if __name__ == '__main__':
    unittest.main()
