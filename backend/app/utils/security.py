import socket
import ipaddress
import urllib.parse
import requests

def _is_safe_ip(ip_str: str) -> bool:
    try:
        ip_obj = ipaddress.ip_address(ip_str)
        # Block private, loopback, multicast, link-local, and unspecified IPs
        if (ip_obj.is_private or ip_obj.is_loopback or
            ip_obj.is_multicast or ip_obj.is_link_local or
            ip_obj.is_unspecified):
            return False
        return True
    except ValueError:
        return False

def is_safe_url(url: str) -> bool:
    try:
        parsed_url = urllib.parse.urlparse(url)
        hostname = parsed_url.hostname
        if not hostname:
            return False

        # Allow basic localhost string but check underlying resolution if possible
        if hostname == 'localhost':
            return False

        # Resolve the hostname to an IP address
        addr_info = socket.getaddrinfo(hostname, None)
        for result in addr_info:
            ip_str = result[4][0]
            if not _is_safe_ip(ip_str):
                return False
        return True
    except (socket.gaierror, ValueError):
        # Hostname resolution failed or invalid IP format
        return False

def safe_requests_get(url: str, **kwargs):
    """
    Secure wrapper around requests.get to prevent SSRF attacks.
    It blocks access to private, loopback, and internal IPs.
    """
    if not is_safe_url(url):
        raise ValueError(f"URL is not safe or resolves to an internal IP: {url}")

    # Remove allow_redirects from kwargs if present, we handle it manually
    kwargs.pop('allow_redirects', None)

    # We validate the initial URL
    session = requests.Session()
    response = session.get(url, allow_redirects=False, **kwargs)

    # Manually follow redirects and validate each step
    max_redirects = kwargs.pop('max_redirects', 5)
    redirects = 0

    while response.is_redirect and redirects < max_redirects:
        next_url = response.headers.get('Location')
        if not next_url:
            break

        # Handle relative redirects
        next_url = urllib.parse.urljoin(response.url, next_url)

        if not is_safe_url(next_url):
            raise ValueError(f"Redirect URL is not safe or resolves to an internal IP: {next_url}")

        response = session.get(next_url, allow_redirects=False, **kwargs)
        redirects += 1

    if response.is_redirect:
        raise ValueError("Too many redirects")

    return response
