import sys
import unittest
import importlib.util
import os
from unittest.mock import MagicMock, patch
from flask import Flask

# 1. Create a mock for 'app' module
# We need this to satisfy 'from app import cache' inside security.py
mock_app = MagicMock()
mock_cache = MagicMock()
mock_app.cache = mock_cache
sys.modules['app'] = mock_app

# 2. Helper to load the module manually
def load_security_module():
    file_path = os.path.join(os.getcwd(), 'backend', 'app', 'utils', 'security.py')
    if not os.path.exists(file_path):
        file_path = os.path.join(os.getcwd(), 'app', 'utils', 'security.py')

    spec = importlib.util.spec_from_file_location("app.utils.security", file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

security_module = load_security_module()
get_client_ip = security_module.get_client_ip
rate_limit = security_module.rate_limit

class TestSecurityUtils(unittest.TestCase):
    def setUp(self):
        self.flask_app = Flask(__name__)

    def test_get_client_ip_direct(self):
        """Test IP detection without proxy"""
        with self.flask_app.test_request_context(environ_base={'REMOTE_ADDR': '1.2.3.4'}):
             self.assertEqual(get_client_ip(), '1.2.3.4')

    def test_rate_limit_pass(self):
        """Test rate limit allowing request"""
        mock_cache.get.return_value = None

        @rate_limit(limit=5)
        def dummy_route():
            return "success"

        with self.flask_app.test_request_context(environ_base={'REMOTE_ADDR': '1.2.3.4'}):
            result = dummy_route()
            self.assertEqual(result, "success")
            mock_cache.set.assert_called()

    def test_rate_limit_fail(self):
        """Test rate limit blocking request"""
        import time
        now = time.time()
        mock_cache.get.return_value = now - 2

        @rate_limit(limit=5)
        def dummy_route():
            return "success"

        with self.flask_app.test_request_context(environ_base={'REMOTE_ADDR': '1.2.3.4'}):
            result = dummy_route()
            # result is (response, 429) tuple
            self.assertTrue(isinstance(result, tuple))
            self.assertEqual(result[1], 429)

if __name__ == '__main__':
    unittest.main()
