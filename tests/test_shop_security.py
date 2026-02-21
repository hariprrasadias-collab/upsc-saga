import unittest
import sqlite3
import os
import sys

# Ensure backend module is importable
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app import create_app
from app.db import get_db

class TestShopSecurity(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()

        # Setup initial state
        conn = get_db()
        # Reset user 1 balance to 1000
        # Check if user 1 exists first
        user = conn.execute("SELECT id FROM users WHERE id = 1").fetchone()
        if not user:
            conn.execute("INSERT INTO users (id, hacksilver) VALUES (1, 1000)")
        else:
            conn.execute("UPDATE users SET hacksilver = 1000 WHERE id = 1")
        conn.commit()

    def tearDown(self):
        self.ctx.pop()

    def test_buy_item_with_manipulated_cost(self):
        # Attempt to buy item with cost 0
        item = {
            "item_id": "leviathan_axe",
            "item_name": "Leviathan Axe (Hack)",
            "cost": 0
        }

        response = self.client.post("/api/shop/buy", json=item)
        self.assertEqual(response.status_code, 200)

        # Verify balance is 800 (1000 - 200), ignoring the 0 cost
        conn = get_db()
        user = conn.execute("SELECT hacksilver FROM users WHERE id = 1").fetchone()
        balance = user['hacksilver']
        self.assertEqual(balance, 800, "Balance should be 800, implying cost was 200 not 0")

    def test_buy_invalid_item(self):
        item = {
            "item_id": "invalid_item",
            "cost": 100
        }
        response = self.client.post("/api/shop/buy", json=item)
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("error", data)

if __name__ == '__main__':
    unittest.main()
