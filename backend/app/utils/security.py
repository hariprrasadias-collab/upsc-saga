from flask import request

def get_real_ip():
    """
    Get the real IP address of the client, even behind proxies.

    Security Note:
    We prefer X-Forwarded-For which is standard on Render/AWS.
    Ideally, we should configure the web server (Gunicorn/Nginx)
    to handle this, but this utility provides a layer of defense
    for application-level rate limiting.
    """
    # X-Forwarded-For: <client>, <proxy1>, <proxy2>
    # Werkzeug's getlist returns ['<client>, <proxy1>, <proxy2>'] if sent as one header
    # or ['<client>', '<proxy1>'] if sent as multiple headers.

    xff = request.headers.getlist("X-Forwarded-For")
    if xff:
        # We take the first element (which might contain commas)
        first_header = xff[0]
        # We split by comma to handle the single-header-multiple-values case
        # and take the first one (the original client IP)
        return first_header.split(',')[0].strip()

    return request.remote_addr

def escape_like_term(term):
    """
    Escape special characters in a SQL LIKE term.
    Escapes %, _, and \.

    Usage:
    safe_term = escape_like_term(user_input)
    cursor.execute("SELECT * FROM t WHERE col LIKE ? ESCAPE '\\'", (f"%{safe_term}%",))
    """
    if not term:
        return term
    return term.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
