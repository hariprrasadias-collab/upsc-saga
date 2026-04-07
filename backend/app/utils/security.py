import requests
import socket
import ipaddress
from urllib.parse import urlparse

def is_safe_url(url: str) -> bool:
    """
    Validates if a URL is safe to fetch (prevents SSRF).
    Checks against private IP ranges, loopback, link-local, multicast.
    """
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ('http', 'https'):
            return False

        hostname = parsed.hostname
        if not hostname:
            return False

        # Resolve hostname to IP
        try:
            ip_addr_str = socket.gethostbyname(hostname)
        except socket.gaierror:
            return False # DNS resolution failed

        ip_addr = ipaddress.ip_address(ip_addr_str)

        if (ip_addr.is_private or
            ip_addr.is_loopback or
            ip_addr.is_link_local or
            ip_addr.is_multicast or
            ip_addr.is_unspecified or
            ip_addr.is_reserved):
            return False

        return True
    except Exception:
        return False

def safe_fetch_url(url: str, timeout: int = 10, headers: dict = None, allow_redirects: bool = True) -> requests.Response:
    """
    Safely fetches a URL after validating it against SSRF.
    Does not blindly follow redirects without re-validating the target URL if manual handling is needed,
    but we use requests' built-in with a check on the initial URL.
    For robust security, one would disable allow_redirects and validate the Location header.
    """
    if not is_safe_url(url):
        raise ValueError(f"Security Policy Violation: Attempted to access forbidden URL: {url}")

    # Use a session to strictly manage redirects
    session = requests.Session()
    session.max_redirects = 3 # Limit redirects

    # If redirects are allowed, we should ideally validate each hop.
    # We will override the session's get_redirect_target to check safety, or just disable automatic redirects and loop.

    # Simple secure approach: Handle redirects manually to check each URL
    current_url = url
    for _ in range(3):
        if not is_safe_url(current_url):
            raise ValueError(f"Security Policy Violation: Redirected to forbidden URL: {current_url}")

        response = session.get(current_url, timeout=timeout, headers=headers, allow_redirects=False)

        if response.is_redirect and allow_redirects:
            current_url = response.headers.get('Location')
            if not current_url.startswith('http'):
                # Handle relative redirects
                from urllib.parse import urljoin
                current_url = urljoin(response.url, current_url)
            continue

        return response

    raise requests.exceptions.TooManyRedirects("Exceeded maximum redirects")
