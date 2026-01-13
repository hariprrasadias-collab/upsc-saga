
def escape_like_term(term):
    """
    Escape special characters for SQL LIKE clauses to prevent wildcard injection.
    Escapes '%', '_', and '\'.

    Usage in SQL: ... LIKE ? ESCAPE '\\'
    """
    if not term:
        return term
    # Escape backslash first to avoid double escaping
    return term.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')

def get_real_ip(request):
    """
    Get the real client IP address, handling proxy headers (X-Forwarded-For).
    Useful when running behind a load balancer (like Render, Nginx).
    """
    if not request:
        return None

    x_forwarded_for = request.headers.get('X-Forwarded-For')
    if x_forwarded_for:
        # The first IP in the list is the original client
        return x_forwarded_for.split(',')[0].strip()

    return request.remote_addr
