import pytest
from app.utils.security import is_safe_url, safe_requests_get

def test_is_safe_url():
    assert is_safe_url("https://www.google.com") == True
    assert is_safe_url("http://example.com/foo") == True

    # Internal / Private
    assert is_safe_url("http://127.0.0.1") == False
    assert is_safe_url("http://localhost:5000") == False
    assert is_safe_url("http://169.254.169.254/latest/meta-data/") == False
    assert is_safe_url("http://10.0.0.1") == False

def test_safe_requests_get_internal():
    # This should throw ValueError immediately without calling requests
    with pytest.raises(ValueError):
        safe_requests_get("http://localhost")
