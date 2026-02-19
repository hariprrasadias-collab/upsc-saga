import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from app import create_app

class TestShopSecurity(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()

    def test_invalid_item_purchase(self):
        """Test that purchasing an invalid item returns 400."""
        payload = {
            "item_id": "non_existent_item",
            "item_name": "Fake Item",
            "cost": 100
        }
        response = self.client.post("/api/shop/buy", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid item", response.get_json().get("error", ""))

    @patch('app.routes.shop.get_db')
    def test_price_manipulation_protection(self, mock_get_db):
        """Test that server uses catalog price instead of client price."""
        # Mock DB connection and user
        mock_conn = MagicMock()
        mock_get_db.return_value = mock_conn

        # Mock user balance to be enough for the real price (200)
        # The query is 'SELECT hacksilver FROM users WHERE id = ?'
        # fetchone() should return a dict-like object
        mock_user = {'hacksilver': 1000}
        mock_conn.execute.return_value.fetchone.return_value = mock_user

        payload = {
            "item_id": "leviathan_axe", # Real price 200
            "item_name": "Leviathan Axe",
            "cost": 1 # Malicious price
        }

        response = self.client.post("/api/shop/buy", json=payload)

        self.assertEqual(response.status_code, 200)

        # Verify that UPDATE used 200, not 1
        # The second call to execute is the UPDATE
        # conn.execute('UPDATE users SET hacksilver = hacksilver - ? WHERE id = ?', (cost, user_id))

        # Check calls
        calls = mock_conn.execute.call_args_list
        update_call = None
        for call in calls:
            if 'UPDATE users' in call[0][0]:
                update_call = call
                break

        self.assertIsNotNone(update_call)
        args = update_call[0][1]
        deducted_amount = args[0]
        self.assertEqual(deducted_amount, 200, "Should deduct catalog price (200), not client price")

if __name__ == '__main__':
    unittest.main()
