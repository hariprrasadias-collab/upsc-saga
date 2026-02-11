import unittest
from unittest.mock import patch, MagicMock
from app.routes.admin import is_admin

class TestAdminSecurity(unittest.TestCase):
    @patch('app.routes.admin.get_db')
    def test_fail_secure_on_db_error(self, mock_get_db):
        """
        Regression Test: Ensure admin access is denied if the database fails.
        This prevents 'Fail Open' vulnerabilities where exceptions grant privileges.
        """
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
