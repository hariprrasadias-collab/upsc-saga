import pytest
from app.utils.security import is_safe_url, safe_requests_get
import requests

def test_is_safe_url():
    # Safe URLs
    assert is_safe_url("https://www.google.com") == True
    assert is_safe_url("http://example.com/path") == True

    # Invalid schemes
    assert is_safe_url("file:///etc/passwd") == False
    assert is_safe_url("ftp://example.com") == False
    assert is_safe_url("gopher://example.com") == False

    # Private / loopback IPv4
    assert is_safe_url("http://127.0.0.1") == False
    assert is_safe_url("http://192.168.1.1") == False
    assert is_safe_url("http://10.0.0.1") == False
    assert is_safe_url("http://0.0.0.0") == False
    assert is_safe_url("http://169.254.169.254") == False

    # Private / loopback IPv6
    assert is_safe_url("http://[::1]") == False
    assert is_safe_url("http://[fd00::1]") == False

def test_safe_requests_get(requests_mock):
    # Test successful request with safe redirects
    requests_mock.get('http://example.com', text='hello', status_code=200)
    resp = safe_requests_get('http://example.com')
    assert resp.text == 'hello'

    # Test redirect to safe URL
    requests_mock.get('http://redirect.com', text='redir', status_code=302, headers={'Location': 'http://example.com'})
    resp = safe_requests_get('http://redirect.com')
    assert resp.text == 'hello'

    # Test redirect to unsafe URL
    requests_mock.get('http://badredirect.com', text='redir', status_code=302, headers={'Location': 'http://127.0.0.1'})
    with pytest.raises(ValueError, match="Unsafe redirect URL encountered"):
        safe_requests_get('http://badredirect.com')

    # Test max redirects
    requests_mock.get('http://loop1.com', text='redir', status_code=302, headers={'Location': 'http://loop2.com'})
    requests_mock.get('http://loop2.com', text='redir', status_code=302, headers={'Location': 'http://loop1.com'})
    with pytest.raises(requests.exceptions.TooManyRedirects):
        safe_requests_get('http://loop1.com', max_redirects=2)
