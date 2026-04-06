import socket
import ipaddress
from urllib.parse import urlparse
import requests

def is_safe_ip(ip_str):
    """Check if an IP address is safe to connect to (not private/loopback/etc)."""
    try:
        ip = ipaddress.ip_address(ip_str)
        # Block private, loopback, multicast, link-local, and unspecified
        if ip.is_private or ip.is_loopback or ip.is_multicast or ip.is_link_local or ip.is_unspecified:
            return False
        return True
    except ValueError:
        return False

def safe_fetch_url(url, timeout=10, headers=None, allow_redirects=True, max_redirects=5):
    """
    Safely fetch a URL preventing SSRF attacks by validating the resolved IP address.
    Also handles redirects manually to ensure each redirect target is safe.
    """
    if not headers:
        headers = {}

    current_url = url
    session = requests.Session()

    for _ in range(max_redirects + 1):
        parsed = urlparse(current_url)
        if parsed.scheme not in ('http', 'https'):
            raise ValueError(f"Invalid schema: {parsed.scheme}")

        hostname = parsed.hostname
        if not hostname:
            raise ValueError("No hostname found in URL")

        # Resolve hostname to IP
        try:
            ip = socket.gethostbyname(hostname)
        except socket.gaierror:
            raise ValueError(f"Could not resolve hostname: {hostname}")

        # Validate IP
        if not is_safe_ip(ip):
            raise ValueError(f"URL resolves to a restricted IP address: {ip}")

        # Perform the request without auto-following redirects
        response = session.get(current_url, timeout=timeout, headers=headers, allow_redirects=False)

        # If it's a redirect and we allow redirects
        if response.is_redirect and allow_redirects:
            next_url = response.headers.get('Location')
            if not next_url:
                return response

            # Handle relative redirects
            if not bool(urlparse(next_url).netloc):
                next_url = f"{parsed.scheme}://{parsed.netloc}{next_url if next_url.startswith('/') else '/' + next_url}"

            current_url = next_url
        else:
            return response

    raise ValueError("Too many redirects")
