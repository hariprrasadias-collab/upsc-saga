import socket
import ipaddress
from urllib.parse import urlparse

def is_safe_url(url: str) -> bool:
    """
    Validates a URL to prevent Server-Side Request Forgery (SSRF) attacks.
    Enforces HTTP/HTTPS schemes and blocks resolution to private, loopback,
    or reserved IP addresses.
    """
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ('http', 'https'):
            return False
        if not parsed.hostname:
            return False

        # Resolve hostname to IP
        # Note: This is a basic defense. In highly secure environments,
        # you might also need to pin the DNS resolution at the request level.
        ip_addr = socket.gethostbyname(parsed.hostname)
        ip = ipaddress.ip_address(ip_addr)

        # Block internal and special-use IP ranges
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_unspecified or ip.is_reserved:
            return False

        return True
    except Exception:
        # Fail securely
        return False
