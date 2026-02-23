## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.

## 2024-05-27 - Hardcoded Session Secret Key
**Vulnerability:** Found a hardcoded `SECRET_KEY` in `backend/app/__init__.py`. This compromises session integrity if deployed.
**Learning:** Developers often hardcode secrets for convenience during initial development. Using `os.environ.get('KEY', 'default')` provides a safe transition path: secure in production (via env vars) while remaining convenient in dev (via default).
**Prevention:** Always use `os.environ.get()` for sensitive configuration from day one. Add a warning log when the default/insecure value is used.
