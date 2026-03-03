from flask import request, jsonify, g
import uuid
import time
import os
import json

# Rate limiting settings
RATE_LIMIT_WINDOW = 60 # seconds
RATE_LIMIT_MAX_REQUESTS = 60

from app.db import BASE_DIR

RATE_LIMIT_FILE = os.environ.get(
    'RATE_LIMIT_FILE', 
    os.path.join(BASE_DIR, 'rate_limits.json')
)

# In-memory rate limit store (avoids file I/O on every request)
_rate_limits: dict = {}
_last_sync = 0.0
_SYNC_INTERVAL = 30  # seconds between file syncs

def _load_rate_limits():
    global _rate_limits
    if os.path.exists(RATE_LIMIT_FILE):
        try:
            with open(RATE_LIMIT_FILE, 'r') as f:
                _rate_limits = json.load(f)
        except (json.JSONDecodeError, IOError):
            _rate_limits = {}
    return _rate_limits

def _save_rate_limits(limits):
    global _last_sync
    now = time.time()
    
    # Only write to disk periodically
    if now - _last_sync < _SYNC_INTERVAL:
        return
    _last_sync = now
    
    try:
        cleaned_limits = {}
        for ip, data in limits.items():
            valid_times = [t for t in data if now - t < RATE_LIMIT_WINDOW]
            if valid_times:
                cleaned_limits[ip] = valid_times
                
        with open(RATE_LIMIT_FILE, 'w') as f:
            json.dump(cleaned_limits, f)
    except Exception as e:
        print(f"Failed to save rate limits: {e}")

def register_middleware(app):
    """
    Registers global application middleware for tracing, rate limiting,
    and standardized API responses.
    """
    
    @app.before_request
    def rate_limiter():
        # Only rate limit API routes
        if not request.path.startswith('/api/'):
            return

        if app.config.get('TESTING') and not app.config.get('TESTING_RATE_LIMITER'):
            return

        client_ip = request.remote_addr
        now = time.time()
        
        # Use in-memory store, load from file only on first request
        global _rate_limits
        if not _rate_limits:
            _load_rate_limits()
        request_times = _rate_limits.get(client_ip, [])
        
        # Filter strictly within window
        request_times = [t for t in request_times if now - t < RATE_LIMIT_WINDOW]
        
        if len(request_times) >= RATE_LIMIT_MAX_REQUESTS:
            return jsonify({
                "success": False,
                "error": "Rate limit exceeded. Try again later."
            }), 429
            
        request_times.append(now)
        _rate_limits[client_ip] = request_times
        
        # Periodic file sync for persistence
        _save_rate_limits(_rate_limits)

    @app.before_request
    def assign_request_id():
        g.request_id = str(uuid.uuid4())

    @app.after_request
    def standardize_response_envelope(response):
        # 1. Always inject the Request ID
        if hasattr(g, 'request_id'):
            response.headers['X-Request-ID'] = g.request_id

        # 2. Only modify JSON API responses
        if not request.path.startswith('/api/'):
            return response

        # Don't try to wrap redirects or files
        if not response.is_json:
            return response

        # If data is already enveloped correctly, skip
        try:
            data = response.get_json()
            if isinstance(data, dict) and 'success' in data and ('data' in data or 'error' in data):
                if 'request_id' not in data:
                    data['request_id'] = g.request_id
                    response.set_data(json.dumps(data))
                return response
        except Exception:
            pass
            
        # Parse the original JSON
        original_data = response.get_json()
        
        # Build standard envelope based on HTTP status
        success = 200 <= response.status_code < 400
        
        envelope = {
            "success": success,
            "request_id": getattr(g, 'request_id', 'unknown')
        }
        
        if success:
            envelope["data"] = original_data
        else:
            envelope["error"] = original_data.get('error', 'Unknown Error') if isinstance(original_data, dict) else str(original_data)

        # Update the response body
        response.set_data(json.dumps(envelope))
        return response
