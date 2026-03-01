
import unittest
import sys
import os
import json

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app import create_app
from app.db import get_db

class AnalyticsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()

    def test_progress_trend_syllabus(self):
        # Test the optimized endpoint
        response = self.client.get('/api/analytics/progress-trend?metric=syllabus&days=30')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertTrue(isinstance(data, list))
        self.assertEqual(len(data), 31) # 30 days + today

        # Check structure
        first_point = data[0]
        self.assertIn('date', first_point)
        self.assertIn('value', first_point)

        # Check that values are consistent (since we know the logic returns a flat line)
        values = [d['value'] for d in data]
        self.assertEqual(len(set(values)), 1, "Expected all values to be the same for syllabus trend")

if __name__ == '__main__':
    unittest.main()
