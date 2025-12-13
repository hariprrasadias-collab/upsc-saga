import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import json

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app import create_app
from app.db import get_db

class TestVisualPersistence(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()

    def test_save_and_retrieve_visual(self):
        # 1. Save Image
        payload = {
            "url": "https://example.com/image.png",
            "prompt": "Test Prompt",
            "seed": 12345,
            "model": "flux",
            "tags": ["test", "unit"]
        }
        res = self.client.post('/api/visual/save', json=payload)
        self.assertEqual(res.status_code, 200)
        
        # 2. Retrieve History
        res = self.client.get('/api/visual/history')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()['data']
        
        # Verify
        found = False
        for item in data:
            if item['url'] == "https://example.com/image.png":
                found = True
                self.assertEqual(item['prompt'], "Test Prompt")
                break
        
        self.assertTrue(found, "Saved image not found in history")

if __name__ == "__main__":
    unittest.main()
