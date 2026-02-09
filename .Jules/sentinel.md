## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.

## 2025-05-15 - Admin Auth Bypass on DB Failure
**Vulnerability:** The `is_admin` check in `backend/app/routes/admin.py` defaulted to allowing access for user ID 1 if a database exception occurred. Since the authentication system currently treats all users as user ID 1, this created a potential privilege escalation vector during database outages.
**Learning:** Defaulting to a "safe" user (like the initial admin) during errors is dangerous if that user has elevated privileges or if authentication is weak. Security checks must always fail closed (deny access).
**Prevention:** Always use a "fail secure" pattern: `try...except...return False`. Never return `True` in an exception block for security checks.

## 2025-05-15 - Module Shadowing on Render
**Vulnerability:** A Render deployment failed because `backend/app.py` conflicted with the `app` package directory during import. This is a common Python pitfall when a script name matches a package name in the same directory.
**Learning:** Avoid naming entrypoint scripts identical to package names (e.g., don't name your main script `app.py` if you have an `app/` package). Use unambiguous names like `wsgi.py` or `main.py`.
**Prevention:** Renamed `backend/app.py` to `backend/wsgi.py` and updated Dockerfile/Start Commands to reference `wsgi:app`.
