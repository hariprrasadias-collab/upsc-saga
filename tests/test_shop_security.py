import os
import sys
import tempfile
import unittest
import sqlite3
import json

# Set up paths
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend'))
sys.path.insert(0, BACKEND_DIR)

# Set DB path for testing BEFORE importing app
fd, db_path = tempfile.mkstemp()
os.environ['DATABASE_PATH'] = db_path

from app import create_app
from app.db import get_db

class TestShopSecurity(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

        with self.app.app_context():
            conn = get_db()
            # Drop the table potentially created by init_core_tables with wrong schema
            conn.execute('DROP TABLE IF EXISTS inventory')

            # Recreate with correct schema expected by shop.py
            conn.execute('''
                CREATE TABLE inventory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    item_id TEXT NOT NULL,
                    item_name TEXT NOT NULL,
                    equipped INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')

            # Initialize minimal schema needed for shop if create_app didn't
            conn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, hacksilver INTEGER, current_xp INTEGER DEFAULT 0, is_admin BOOLEAN DEFAULT 0)')

            # Create user 1 with 1000 hacksilver
            conn.execute('DELETE FROM users WHERE id = 1')
            conn.execute('INSERT INTO users (id, username, hacksilver) VALUES (1, "testuser", 1000)')
            conn.commit()

    def tearDown(self):
        # Clean up is handled by tempfile but good practice to close
        pass

    def test_buy_item_price_manipulation(self):
        """
        Test that a user cannot buy an item for a manipulated price.
        Attempts to buy an item worth 200 for 1.
        """
        print("\n--- Testing Shop Security ---")

        # Attempt to buy 'leviathan_axe' (real cost 200) for 1 hacksilver
        # This simulates a manipulated request from the client
        response = self.client.post('/api/shop/buy', json={
            'item_id': 'leviathan_axe',
            'item_name': 'Leviathan Axe',
            'cost': 1
        })

        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.get_json()}")

        with self.app.app_context():
            conn = get_db()
            user = conn.execute('SELECT hacksilver FROM users WHERE id = 1').fetchone()
            balance = user['hacksilver']
            print(f"User Balance after purchase: {balance}")

            # If vulnerable: 1000 - 1 = 999
            if balance == 999:
                 self.fail(f"SECURITY VULNERABILITY DETECTED: Item purchased for client-supplied cost (1) instead of real cost (200). Balance: {balance}")

            # If secure, it should be 800 (1000 - 200)
            self.assertEqual(balance, 800, f"Should charge the real cost (200). Actual balance: {balance}")

if __name__ == '__main__':
    # Run tests
    unittest.main()
