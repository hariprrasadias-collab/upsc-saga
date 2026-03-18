import socket
import ipaddress
from urllib.parse import urlparse
import requests

def is_safe_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ('http', 'https'):
            return False
        if not parsed.hostname:
            return False
        ip = socket.gethostbyname(parsed.hostname)
        parsed_ip = ipaddress.ip_address(ip)
        return not (parsed_ip.is_private or parsed_ip.is_loopback or parsed_ip.is_reserved)
    except Exception:
        return False

def safe_get(url: str, **kwargs):
    kwargs['allow_redirects'] = False
    current_url = url
    for _ in range(5):
        if not is_safe_url(current_url):
            raise ValueError("Unsafe or invalid URL")

        resp = requests.get(current_url, **kwargs)
        if resp.is_redirect:
            redirect_url = resp.headers.get('Location')
            if not redirect_url:
                raise ValueError("Redirect missing Location header")
            # Handle relative redirects
            parsed_redirect = urlparse(redirect_url)
            if not parsed_redirect.netloc:
                parsed_current = urlparse(current_url)
                current_url = f"{parsed_current.scheme}://{parsed_current.netloc}{redirect_url}"
            else:
                current_url = redirect_url
        else:
            return resp
    raise ValueError("Too many redirects")
