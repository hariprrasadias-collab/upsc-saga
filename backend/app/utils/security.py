import urllib.parse
import ipaddress
import socket
import requests

def is_safe_url(url):
    try:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in ('http', 'https'):
            return False

        hostname = parsed.hostname
        if not hostname:
            return False

        # Helper to check if an IP is unsafe
        def is_unsafe_ip(ip):
            if ip.is_loopback or ip.is_private or ip.is_reserved or ip.is_multicast:
                return True
            if ip.is_link_local or ip.is_unspecified:
                return True
            if not getattr(ip, 'is_global', True):
                return True
            return False

        # Try direct IP parsing first
        try:
            ip = ipaddress.ip_address(hostname)
            if is_unsafe_ip(ip):
                return False
            return True
        except ValueError:
            pass

        # Resolve all addresses (IPv4 and IPv6)
        try:
            # getaddrinfo returns a list of 5-tuples: (family, type, proto, canonname, sockaddr)
            # sockaddr for IPv4 is a 2-tuple (address, port)
            # sockaddr for IPv6 is a 4-tuple (address, port, flow info, scope id)
            addrinfo = socket.getaddrinfo(hostname, None)

            # If any of the resolved IPs are unsafe, consider the URL unsafe
            # because an attacker might control DNS to return multiple IPs,
            # hoping the HTTP client picks the unsafe one.
            for info in addrinfo:
                ip_str = info[4][0]
                ip = ipaddress.ip_address(ip_str)
                if is_unsafe_ip(ip):
                    return False

        except socket.gaierror:
            return False

        return True
    except Exception:
        return False

def safe_requests_get(url, **kwargs):
    """
    Wrapper for requests.get that safely follows redirects while verifying
    that each redirect target is also a safe URL.
    """
    if not is_safe_url(url):
        raise ValueError(f"Unsafe URL provided: {url}")

    # Don't let requests follow redirects automatically so we can check them
    kwargs['allow_redirects'] = False

    max_redirects = kwargs.pop('max_redirects', 10)
    redirects = 0

    current_url = url
    session = requests.Session()

    while redirects <= max_redirects:
        resp = session.get(current_url, **kwargs)

        if resp.is_redirect:
            redirects += 1
            # Get the redirect location
            location = resp.headers.get('Location')
            if not location:
                # Should not happen typically, but if it does, stop
                return resp

            # Resolve relative redirects
            next_url = urllib.parse.urljoin(current_url, location)

            # Verify the new URL is safe
            if not is_safe_url(next_url):
                raise ValueError(f"Unsafe redirect URL encountered: {next_url}")

            current_url = next_url
        else:
            return resp

    raise requests.exceptions.TooManyRedirects(f"Exceeded {max_redirects} redirects.")
