## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.

## 2024-05-24 - Hardcoded Secrets & Cookie Security
**Vulnerability:** The application was using a hardcoded `SECRET_KEY` in the Flask configuration (`backend/app/__init__.py`), which would allow session hijacking if the code were leaked. Additionally, session cookies lacked security flags like `HttpOnly`, `SameSite`, and `Secure`.
**Learning:** Defaulting to a hardcoded key in the source code ("for development") is a dangerous pattern because it often makes it into production.
**Prevention:** Always use `os.environ.get()` for sensitive keys. Explicitly configure session cookie security headers (`SESSION_COOKIE_HTTPONLY=True`, `SESSION_COOKIE_SAMESITE='Lax'`, `SESSION_COOKIE_SECURE=True` in prod) to prevent XSS/CSRF attacks on sessions.
