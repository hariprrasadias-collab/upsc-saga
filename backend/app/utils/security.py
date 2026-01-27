from functools import wraps
from flask import request, jsonify
from app import cache
import time

def get_client_ip():
    """
    Safely get the client IP address.
    Relies on Werkzeug's ProxyFix middleware (configured in app/__init__.py)
    to correctly populate request.remote_addr from X-Forwarded-For.
    """
    return request.remote_addr

def rate_limit(limit=5, key_func=get_client_ip):
    """
    Simple rate limiting decorator using Flask-Caching.
    Enforces a cooldown period of `limit` seconds between requests for the same key.

    Args:
        limit (int): Cooldown in seconds.
        key_func (callable): Function to generate unique key (default: IP).
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            try:
                # Generate cache key
                identifier = key_func()
                # Use function name to allow independent limits per endpoint
                key = f"rate_limit:{f.__name__}:{identifier}"

                # Check cache
                last_req = cache.get(key)
                current_time = time.time()

                if last_req:
                    time_passed = current_time - last_req
                    if time_passed < limit:
                        wait_time = int(limit - time_passed) + 1
                        return jsonify({
                            'success': False,
                            'error': f'Rate limit exceeded. Please wait {wait_time} seconds.'
                        }), 429

                # Update cache
                cache.set(key, current_time, timeout=limit)

            except Exception as e:
                # Fail open if cache fails (don't block user on system error)
                print(f"Rate limit check error: {e}")

            return f(*args, **kwargs)
        return wrapped
    return decorator
