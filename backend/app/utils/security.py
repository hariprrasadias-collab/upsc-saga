from functools import wraps
from flask import request, jsonify

# Use relative import to avoid shadowing 'app' package with 'app.py' module
# This imports 'cache' from 'app/__init__.py'
from .. import cache

def rate_limit(limit, per):
    """
    Rate limiting decorator using the global cache.
    limit: Number of requests allowed
    per: Time window in seconds
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Use remote_addr as identifier
            identifier = request.remote_addr
            key = f"rate_limit:{request.endpoint}:{identifier}"

            # SimpleCache get/set
            current = cache.get(key)
            try:
                count = int(current) if current is not None else 0
            except (ValueError, TypeError):
                count = limit # Fail safe

            if count >= limit:
                return jsonify({
                    'success': False,
                    'error': f'Rate limit exceeded. Try again in {per} seconds.'
                }), 429

            cache.set(key, count + 1, timeout=per)

            return f(*args, **kwargs)
        return wrapped
    return decorator
