
import unittest
import sqlite3
import os
import json
from datetime import datetime

# Add backend directory to path
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.db import get_db

class TestPomodoroLevelUp(unittest.TestCase):
    def setUp(self):
        # Use a test database
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['DATABASE'] = ':memory:'
        self.client = self.app.test_client()

        with self.app.app_context():
            from app.db_models.core import init_core_tables

            # Initialize core tables (includes users)
            # We need to manually initialize because init_core_tables connects to get_db()
            # which uses app.config['DATABASE']

            # Since create_pomodoro_table.py hardcodes the DB name, we should recreate the table manually
            # or modify the function. For this test, let's just create the table in our memory DB.
            conn = get_db()
            conn.execute('''
                CREATE TABLE IF NOT EXISTS pomodoro_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER DEFAULT 1,
                    timestamp TEXT,
                    duration INTEGER,
                    xp_awarded INTEGER
                )
            ''')
            conn.commit()

            # Initialize core tables
            init_core_tables()

    def test_single_level_up(self):
        with self.app.app_context():
            conn = get_db()
            # Setup User: Level 1, 90 XP (Needs 100 for Lvl 2)
            conn.execute('UPDATE users SET level = 1, current_xp = 90, max_xp = 100 WHERE id = 1')
            conn.commit()

        # Action: Complete Pomodoro (Awards 50 XP)
        response = self.client.post('/api/pomodoro/complete', json={
            'duration': 1500,
            'timestamp': datetime.now().isoformat()
        })

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['level_up'])
        self.assertEqual(data['new_level'], 2)

        with self.app.app_context():
            conn = get_db()
            cursor = conn.execute('SELECT level, current_xp FROM users WHERE id = 1')
            user = cursor.fetchone()
            # 90 + 50 = 140. Lvl 1->2 costs 100. Remainder 40.
            self.assertEqual(user['level'], 2)
            self.assertEqual(user['current_xp'], 40)

    def test_multiple_level_up_bug(self):
        """
        Test case to verify the bug where multiple level ups are not handled.
        """
        with self.app.app_context():
            conn = get_db()
            # Setup User: Level 1, 350 XP (Enough for Level 3)
            # Lvl 1 (100) -> Lvl 2 (200) -> Lvl 3 (300)
            # 350 - 100 (Lvl 1) = 250 XP remaining.
            # 250 - 200 (Lvl 2) = 50 XP remaining.
            # Should end up at Level 3 with 50 XP.

            # Note: The route adds 50 XP. So if we start with 350, we have 400.
            # 400 - 100 = 300.
            # 300 - 200 = 100.
            # Should end up at Level 3 with 100 XP.
            conn.execute('UPDATE users SET level = 1, current_xp = 350, max_xp = 100 WHERE id = 1')
            conn.commit()

        # Action: Complete Pomodoro (Awards 50 XP) -> Total 400 XP
        response = self.client.post('/api/pomodoro/complete', json={
            'duration': 1500,
            'timestamp': datetime.now().isoformat()
        })

        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        with self.app.app_context():
            conn = get_db()
            cursor = conn.execute('SELECT level, current_xp, max_xp FROM users WHERE id = 1')
            user = cursor.fetchone()

            print(f"User State: Level {user['level']}, XP {user['current_xp']}")

            self.assertEqual(user['level'], 3, f"Expected Level 3, but got Level {user['level']}")
            # Level 3 Max XP should be 300 (3 * 100)
            self.assertEqual(user['current_xp'], 100, f"Expected 100 XP, but got {user['current_xp']}")

if __name__ == '__main__':
    unittest.main()
