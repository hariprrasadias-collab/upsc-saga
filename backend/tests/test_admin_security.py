import pytest
from unittest.mock import MagicMock, patch
from backend.app.routes.admin import is_admin

def test_is_admin_safe_fail():
    """
    Test that is_admin fails SAFELY (returns False) when the database query fails.
    Currently, the code has a vulnerability where it defaults to True for user_id=1.
    We are asserting the DESIRED behavior (False), so this test is expected to FAIL
    until we fix the vulnerability.
    """
    # Mock get_db to raise an exception
    with patch('backend.app.routes.admin.get_db') as mock_get_db:
        mock_get_db.side_effect = Exception("Database connection failed")

        # Test with user_id=1 (the vulnerable case)
        # This is expected to return True in the current vulnerable code
        # But we want it to return False
        result = is_admin(1)

        assert result is False, "is_admin(1) should return False on DB error, but returned True (Fail Open Vulnerability)"

def test_is_admin_safe_fail_other_user():
    """
    Test that is_admin fails SAFELY for other users too.
    """
    with patch('backend.app.routes.admin.get_db') as mock_get_db:
        mock_get_db.side_effect = Exception("Database connection failed")
        result = is_admin(2)
        assert result is False
