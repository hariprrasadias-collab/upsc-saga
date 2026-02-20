import sys
import os
import pytest
from unittest.mock import patch

# Add backend to sys.path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.routes.admin import is_admin

def test_is_admin_fail_secure_user_1():
    """
    Test that is_admin returns False when a database error occurs,
    even for user_id 1.
    """
    with patch('app.routes.admin.get_db') as mock_get_db:
        mock_get_db.side_effect = Exception("Database connection failed")

        # Expect False for secure implementation
        result = is_admin(1)
        assert result is False, f"Security Vulnerability: is_admin(1) returned {result} on DB error"

def test_is_admin_fail_secure_other_user():
    with patch('app.routes.admin.get_db') as mock_get_db:
        mock_get_db.side_effect = Exception("Database connection failed")
        assert is_admin(2) is False
