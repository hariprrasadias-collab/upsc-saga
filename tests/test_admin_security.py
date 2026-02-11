import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add backend to path so we can import app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

try:
    from app.routes.admin import is_admin
except ImportError as e:
    print(f"ImportError: {e}")
    sys.exit(1)

class TestAdminSecurity(unittest.TestCase):
    @patch('app.routes.admin.get_db')
    def test_fail_secure(self, mock_get_db):
        """
        Test that is_admin fails securely (returns False) when database is unavailable.
        Previously, it failed open (returned True) for user_id=1.
        """
        # Mock get_db to raise an exception
        mock_get_db.side_effect = Exception("Database connection failed")

        # Call is_admin with user_id=1
        is_admin_result = is_admin(1)

        print(f"is_admin(1) returned: {is_admin_result}")

        # Assert that it returns False (Fail Secure)
        self.assertFalse(is_admin_result, "is_admin(1) should return False (Fail Secure) on DB error")

if __name__ == '__main__':
    unittest.main()
