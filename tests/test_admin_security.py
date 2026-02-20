import sys
import os
import unittest
from unittest.mock import patch

# Add backend to sys.path
# Assuming the test is run from project root
current_dir = os.getcwd()
backend_dir = os.path.join(current_dir, 'backend')
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

try:
    from app.routes.admin import is_admin
except ImportError:
    # Fallback if structure is different
    pass

class TestAdminSecurity(unittest.TestCase):
    def test_is_admin_fail_secure_user_1(self):
        """
        Test that is_admin returns False when a database error occurs,
        even for user_id 1.
        """
        with patch('app.routes.admin.get_db') as mock_get_db:
            mock_get_db.side_effect = Exception("Database connection failed")

            # Expect False for secure implementation
            result = is_admin(1)
            self.assertFalse(result, f"Security Vulnerability: is_admin(1) returned {result} on DB error")

    def test_is_admin_fail_secure_other_user(self):
        with patch('app.routes.admin.get_db') as mock_get_db:
            mock_get_db.side_effect = Exception("Database connection failed")
            self.assertFalse(is_admin(2))

if __name__ == '__main__':
    unittest.main()
