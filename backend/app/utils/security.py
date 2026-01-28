from functools import wraps
from flask import request, jsonify
from app import cache

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

            current = cache.get(key)
            try:
                count = int(current) if current is not None else 0
            except (ValueError, TypeError):
                count = limit # Fail safe: block if corrupt

            if count >= limit:
                return jsonify({
                    'success': False,
                    'error': f'Rate limit exceeded. Try again in {per} seconds.'
                }), 429

            # Increment and set
            # Note: This resets the timeout window on every successful request.
            # For limit=1, this acts as a cooldown from the last successful request.
            cache.set(key, count + 1, timeout=per)

            return f(*args, **kwargs)
        return wrapped
    return decorator
