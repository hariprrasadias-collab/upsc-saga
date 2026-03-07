import urllib.parse
import ipaddress
import socket

def is_safe_url(url: str) -> bool:
    """
    Validates a URL to prevent SSRF (Server-Side Request Forgery).
    Only allows HTTP/HTTPS and blocks resolution to internal or private IP addresses.
    """
    try:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in ['http', 'https']:
            return False

        hostname = parsed.hostname
        if not hostname:
            return False

        # Basic blocklist for hostnames
        if hostname.lower() in ['localhost', '127.0.0.1', '0.0.0.0', '[::1]']:
            return False

        # Resolve IP to block internal networks
        addr_info = socket.getaddrinfo(hostname, None)
        for res in addr_info:
            ip = res[4][0]
            ip_obj = ipaddress.ip_address(ip)
            if (ip_obj.is_loopback or
                ip_obj.is_private or
                ip_obj.is_multicast or
                ip_obj.is_reserved or
                ip_obj.is_link_local):
                return False
        return True
    except Exception:
        return False
