import pytest
from app.utils.security import is_safe_url, safe_get
import requests_mock

def test_is_safe_url():
    assert is_safe_url("https://google.com") == True
    assert is_safe_url("http://127.0.0.1") == False
    assert is_safe_url("http://localhost") == False
    assert is_safe_url("http://192.168.1.1") == False
    assert is_safe_url("http://10.0.0.1") == False
    assert is_safe_url("file:///etc/passwd") == False

def test_safe_get_valid():
    with requests_mock.Mocker() as m:
        m.get('https://google.com', text='OK')
        resp = safe_get('https://google.com')
        assert resp.text == 'OK'

def test_safe_get_redirect():
    with requests_mock.Mocker() as m:
        m.get('https://example.com/1', status_code=302, headers={'Location': 'https://example.com/2'})
        m.get('https://example.com/2', text='Redirected')
        resp = safe_get('https://example.com/1')
        assert resp.text == 'Redirected'

def test_safe_get_unsafe_redirect():
    with requests_mock.Mocker() as m:
        m.get('https://example.com/1', status_code=302, headers={'Location': 'http://127.0.0.1'})
        with pytest.raises(ValueError):
            safe_get('https://example.com/1')
