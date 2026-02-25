import unittest
import json
from app import create_app
from app.db import get_db

class ShopSecurityTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()

        # Reset user 1 balance
        conn = get_db()
        # Ensure user 1 exists (it should be seeded by create_app -> init_core_tables)
        user = conn.execute('SELECT * FROM users WHERE id = 1').fetchone()
        if not user:
            conn.execute("INSERT INTO users (id, username, hacksilver) VALUES (1, 'TestUser', 1000)")
        else:
            conn.execute('UPDATE users SET hacksilver = 1000 WHERE id = 1')
        conn.commit()

    def tearDown(self):
        self.ctx.pop()

    def test_price_manipulation(self):
        """Test that client-provided cost is ignored."""
        initial_balance = 1000

        # Attempt to buy Leviathan Axe (cost 200) for 0 cost
        payload = {
            'item_id': 'leviathan_axe',
            'item_name': 'Leviathan Axe',
            'cost': 0
        }

        response = self.client.post('/api/shop/buy',
                                  data=json.dumps(payload),
                                  content_type='application/json')

        self.assertEqual(response.status_code, 200)

        # Check database for actual deduction
        conn = get_db()
        user = conn.execute('SELECT hacksilver FROM users WHERE id = 1').fetchone()

        # Balance should be 800 (1000 - 200), NOT 1000
        self.assertEqual(user['hacksilver'], 800, "Price manipulation succeeded! Balance should be 800.")

    def test_invalid_item(self):
        """Test that invalid item IDs are rejected."""
        payload = {
            'item_id': 'non_existent_item',
            'cost': 0
        }

        response = self.client.post('/api/shop/buy',
                                  data=json.dumps(payload),
                                  content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid Item ID', response.get_json()['error'])

if __name__ == '__main__':
    unittest.main()
