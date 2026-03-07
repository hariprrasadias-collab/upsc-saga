
import unittest
from unittest.mock import MagicMock, patch
from app.routes.admin import is_admin

class TestAdminFailOpen(unittest.TestCase):
    @patch('app.routes.admin.get_db')
    def test_fail_securely_on_db_error(self, mock_get_db):
        """
        Verify that is_admin returns False (Fail Closed) when a database error occurs,
        instead of failing open for user_id=1.
        """
        # Simulate a database error (e.g., connection lost, syntax error)
        mock_get_db.side_effect = Exception("DB Connection Failed")

        # Test for user 1 (previously vulnerable)
        self.assertFalse(is_admin(1), "is_admin(1) should return False on DB error")

        # Test for other users (always safe)
        self.assertFalse(is_admin(2), "is_admin(2) should return False on DB error")

if __name__ == '__main__':
    unittest.main()
