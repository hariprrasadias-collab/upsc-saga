
import unittest
import sqlite3
import os
import json
import sys

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.db import get_db

class TestTaskLogBug(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['DATABASE'] = ':memory:'
        self.client = self.app.test_client()

        with self.app.app_context():
            from app.db_models.core import init_core_tables
            init_core_tables()
            # Note: We are NOT manually creating activity_log here.
            # We want to confirm it fails if the app expects it but it's not created by init_core_tables.

    def test_log_study_session_missing_table(self):
        """
        Test that logging a study session fails because the table is missing
        AND/OR fails because the code is buggy (unreachable commit).
        """
        response = self.client.post('/api/tasks/log-study', json={
            'minutes': 60
        })

        # If the table is missing, this should be 500
        if response.status_code == 500:
            print("Confirmed: 500 Error (likely missing table)")
            data = response.get_json()
            if data and 'error' in data:
                print(f"Error message: {data['error']}")
                if 'no such table: activity_log' in data['error']:
                    print("✅ Bug Verified: Table 'activity_log' is missing.")
        else:
            print(f"Unexpected status code: {response.status_code}")

        # If by miracle it passes (e.g., if I was wrong and table exists),
        # we check if data was actually committed (the second bug).
        if response.status_code == 200:
            with self.app.app_context():
                conn = get_db()
                try:
                    logs = conn.execute('SELECT * FROM activity_log').fetchall()
                    if len(logs) == 0:
                        print("✅ Bug Verified: Data was not committed to DB (Unreachable code).")
                    else:
                        print("❌ Bug Not Reproduced: Data was found in DB.")
                except Exception as e:
                    print(f"Checking DB failed: {e}")

if __name__ == '__main__':
    unittest.main()
