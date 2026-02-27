
import unittest
from flask import Flask, request
from app.utils.security import get_real_ip, escape_like_term

class TestSecurityUtils(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)

    def test_get_real_ip_with_x_forwarded_for(self):
        with self.app.test_request_context(headers={'X-Forwarded-For': '10.0.0.1, 10.0.0.2'}):
            ip = get_real_ip()
            self.assertEqual(ip, '10.0.0.1')

    def test_get_real_ip_without_x_forwarded_for(self):
        with self.app.test_request_context(environ_base={'REMOTE_ADDR': '127.0.0.1'}):
            ip = get_real_ip()
            self.assertEqual(ip, '127.0.0.1')

    def test_escape_like_term(self):
        self.assertEqual(escape_like_term('normal'), 'normal')
        self.assertEqual(escape_like_term('100%'), '100\\%')
        self.assertEqual(escape_like_term('a_b'), 'a\\_b')
        self.assertEqual(escape_like_term('C:\\path'), 'C:\\\\path')
        self.assertEqual(escape_like_term(''), '')
        self.assertIsNone(escape_like_term(None))

if __name__ == '__main__':
    unittest.main()
