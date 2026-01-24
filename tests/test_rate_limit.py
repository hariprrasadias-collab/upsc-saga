import sys
import os
import unittest
from unittest.mock import MagicMock, patch
from flask import Flask, request
import time

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

class TestRateLimit(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)

    def test_get_client_ip(self):
        try:
            from app.routes.pyq import get_client_ip
        except ImportError:
            self.fail("get_client_ip not found in app.routes.pyq")

        # Case 1: X-Forwarded-For with multiple IPs
        with self.app.test_request_context(headers={'X-Forwarded-For': '203.0.113.195, 70.41.3.18'}):
            ip = get_client_ip()
            self.assertEqual(ip, '203.0.113.195')

        # Case 2: X-Forwarded-For with single IP
        with self.app.test_request_context(headers={'X-Forwarded-For': '10.0.0.5'}):
            ip = get_client_ip()
            self.assertEqual(ip, '10.0.0.5')

        # Case 3: No X-Forwarded-For, use REMOTE_ADDR
        with self.app.test_request_context(environ_base={'REMOTE_ADDR': '127.0.0.1'}):
            ip = get_client_ip()
            self.assertEqual(ip, '127.0.0.1')

    def test_cleanup_rate_limit(self):
        try:
            from app.routes.pyq import cleanup_rate_limit, _strategos_rate_limit
        except ImportError:
            self.fail("cleanup_rate_limit not found in app.routes.pyq")

        # Setup stale data
        _strategos_rate_limit.clear()
        _strategos_rate_limit['stale_ip'] = time.time() - 100
        _strategos_rate_limit['fresh_ip'] = time.time()

        cleanup_rate_limit()

        self.assertNotIn('stale_ip', _strategos_rate_limit)
        self.assertIn('fresh_ip', _strategos_rate_limit)

if __name__ == '__main__':
    unittest.main()
