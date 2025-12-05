
import unittest
import sqlite3
import os
import json
import sys

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.db import get_db

class TestShopSecurity(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['DATABASE'] = ':memory:'
        self.client = self.app.test_client()

        with self.app.app_context():
            from app.db_models.core import init_core_tables
            init_core_tables()

            conn = get_db()
            try:
                conn.execute('ALTER TABLE inventory ADD COLUMN item_name TEXT')
            except:
                pass
            try:
                conn.execute('ALTER TABLE inventory ADD COLUMN equipped INTEGER DEFAULT 0')
            except:
                pass

            # Set initial hacksilver
            conn.execute('UPDATE users SET hacksilver = 100 WHERE id = 1')
            conn.commit()

    def test_prevent_negative_cost_purchase(self):
        """
        Test that a user CANNOT exploit the buy endpoint by sending a negative cost.
        Expects 400 Error.
        """
        initial_balance = 100
        exploit_cost = -500

        response = self.client.post('/api/shop/buy', json={
            'item_id': 'exploit_sword',
            'item_name': 'Sword of Exploitation',
            'cost': exploit_cost
        })

        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid cost', response.get_json()['error'])

        with self.app.app_context():
            conn = get_db()
            user = conn.execute('SELECT hacksilver FROM users WHERE id = 1').fetchone()
            new_balance = user['hacksilver']
            self.assertEqual(new_balance, initial_balance)

    def test_valid_purchase(self):
        """Test a valid purchase works"""
        response = self.client.post('/api/shop/buy', json={
            'item_id': 'valid_sword',
            'item_name': 'Valid Sword',
            'cost': 50
        })
        self.assertEqual(response.status_code, 200)

        with self.app.app_context():
            conn = get_db()
            user = conn.execute('SELECT hacksilver FROM users WHERE id = 1').fetchone()
            self.assertEqual(user['hacksilver'], 50)

if __name__ == '__main__':
    unittest.main()
