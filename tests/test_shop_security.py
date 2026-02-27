import unittest
import os
import json
import sqlite3
import tempfile
import sys

# Add backend to path so we can import app modules
# Assuming this file is in tests/ and backend/ is sibling
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from app import create_app
from app.db import get_db, init_app

class TestShopSecurity(unittest.TestCase):
    def setUp(self):
        # Create a temporary file for the database
        self.db_fd, self.db_path = tempfile.mkstemp()
        os.environ['DATABASE_PATH'] = self.db_path

        self.app = create_app()
        self.client = self.app.test_client()

        with self.app.app_context():
            # Initialize core tables
            from app.db_models.core import init_core_tables
            init_core_tables()

            conn = get_db()
            # Manually add columns expected by shop.py if they don't exist
            # because init_core_tables seems to be missing them based on my read
            try:
                conn.execute('ALTER TABLE inventory ADD COLUMN item_name TEXT')
            except sqlite3.OperationalError:
                pass # Column might exist

            try:
                conn.execute('ALTER TABLE inventory ADD COLUMN equipped BOOLEAN DEFAULT 0')
            except sqlite3.OperationalError:
                pass

            # Ensure user 1 has enough money
            conn.execute('UPDATE users SET hacksilver = 1000 WHERE id = 1')
            conn.commit()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_buy_item_manipulated_cost(self):
        """
        Test that buying an item with a manipulated cost (lower than real price)
        fails or charges the correct amount.
        """
        # Leviathan Axe costs 200 normally.
        # We try to buy it for 0.
        payload = {
            "item_id": "leviathan_axe",
            "item_name": "Leviathan Axe",
            "cost": 0
        }

        response = self.client.post('/api/shop/buy',
                                  data=json.dumps(payload),
                                  content_type='application/json')

        # In the vulnerable version, this returns 200 and deducts 0.
        # In the fixed version, this should either:
        # 1. Return 200 but deduct 200 (ignoring client cost)
        # 2. Return 400 because cost doesn't match (if we add that check)
        # The plan is to IGNORE client cost and use server cost.

        # Let's check the user's balance after purchase
        with self.app.app_context():
            conn = get_db()
            user = conn.execute('SELECT hacksilver FROM users WHERE id = 1').fetchone()
            # Initial was 1000. Real cost is 200.
            # If vulnerable: 1000 (cost 0)
            # If fixed: 800 (cost 200)

            # Since I haven't fixed it yet, this assertion is expected to FAIL if I assert 800.
            # But I will write the test to assert the FIXED behavior.
            self.assertEqual(user['hacksilver'], 800,
                             f"Security Check Failed: User balance is {user['hacksilver']}, expected 800. "
                             "The server likely accepted the manipulated cost of 0.")

    def test_buy_invalid_item(self):
        """Test buying an item not in the catalog"""
        payload = {
            "item_id": "non_existent_item",
            "item_name": "Fake Item",
            "cost": 10
        }
        response = self.client.post('/api/shop/buy',
                                  data=json.dumps(payload),
                                  content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid item", response.get_json().get('error', ''))

if __name__ == '__main__':
    unittest.main()
