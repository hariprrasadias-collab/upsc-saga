import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add backend to path if not present, to allow import
backend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend')
if backend_path not in sys.path:
    sys.path.append(backend_path)

class TestAdminSecurity(unittest.TestCase):
    def test_fail_secure_on_db_error(self):
        """
        Regression Test: Ensure admin access is denied if the database fails.
        This prevents 'Fail Open' vulnerabilities where exceptions grant privileges.
        """
        try:
            from app.routes.admin import is_admin
        except ImportError:
            self.skipTest("Could not import app.routes.admin")

        with patch('app.routes.admin.get_db') as mock_get_db:
            # Simulate a database failure
            mock_get_db.side_effect = Exception("Database Connection Failed")

            # Check if user_id=1 is granted admin access despite the failure
            # Desired secure behavior: returns False
            result = is_admin(1)

            print(f"\n[Test] is_admin(1) with DB failure returned: {result}")

            # Assert that access is denied
            self.assertFalse(result, "SECURITY REGRESSION: Admin access granted during DB failure!")

if __name__ == '__main__':
    unittest.main()
