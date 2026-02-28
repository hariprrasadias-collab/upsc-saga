# app/utils/session.py
"""
Session management utilities.
Currently returns hardcoded user_id = 1.
TODO: Replace with proper Flask-Login or JWT authentication.
"""

def get_current_user_id():
    """
    Get the current authenticated user's ID.
    
    Returns:
        int: User ID (currently hardcoded to 1)
    
    TODO: Implement proper session management
    - Flask-Login for session-based auth
    - Or JWT tokens for stateless auth
    - Read from Flask session or decode JWT
    """
    # Hardcoded for now - will be replaced with:
    # return session.get('user_id') or jwt_decode(request.headers.get('Authorization'))
    return 1


from functools import wraps

def require_auth(func):
    """
    Decorator to require authentication for a route.
    
    TODO: Implement proper authentication check
    - Check if user is logged in
    - Return 401 if not authenticated
    - Pass user_id to the wrapped function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = get_current_user_id()
        if not user_id:
            from flask import jsonify
            return jsonify({'error': 'Authentication required'}), 401
        return func(*args, user_id=user_id, **kwargs)
    return wrapper
