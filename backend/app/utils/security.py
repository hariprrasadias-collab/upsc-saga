import ipaddress
import socket
from urllib.parse import urlparse
import requests
from requests.exceptions import RequestException

class SSRFError(RequestException):
    pass

def is_safe_ip(ip_str):
    try:
        ip = ipaddress.ip_address(ip_str)
        # Block private, loopback, multicast, link-local, unspecified, and reserved IPs
        if ip.is_private or ip.is_loopback or ip.is_multicast or ip.is_link_local or ip.is_unspecified or getattr(ip, 'is_reserved', False):
            return False
        return True
    except ValueError:
        return False

def resolve_and_check_url(url):
    parsed = urlparse(url)
    hostname = parsed.hostname
    if not hostname:
        raise SSRFError("Invalid URL")

    try:
        addr_info = socket.getaddrinfo(hostname, None)
    except socket.gaierror:
        raise SSRFError(f"Could not resolve hostname {hostname}")

    for info in addr_info:
        ip = info[4][0]
        if not is_safe_ip(ip):
            raise SSRFError(f"Blocked request to forbidden IP: {ip}")

    return True

def safe_requests_get(url, **kwargs):
    """
    A safe wrapper around requests.get that mitigates SSRF attacks by preventing
    requests to private, loopback, and other reserved IP addresses, even after redirects.
    """
    session = requests.Session()
    timeout = kwargs.pop('timeout', 10)

    current_url = url
    max_redirects = 5

    for _ in range(max_redirects):
        resolve_and_check_url(current_url)

        call_kwargs = dict(kwargs)
        call_kwargs['allow_redirects'] = False
        call_kwargs['timeout'] = timeout

        response = session.get(current_url, **call_kwargs)

        if response.is_redirect:
            next_url = response.headers.get('Location')
            if not next_url:
                break
            from urllib.parse import urljoin
            current_url = urljoin(current_url, next_url)
        else:
            return response

    raise SSRFError("Too many redirects")
