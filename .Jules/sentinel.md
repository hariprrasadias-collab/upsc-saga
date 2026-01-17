## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.

## 2025-02-26 - Hardcoded Secrets & Auth Bypass
**Vulnerability:** The Flask secret key was hardcoded in `__init__.py`, and `get_current_user_id()` in `session.py` was hardcoded to `1`, granting admin access to all users.
**Learning:** Hardcoding "dev" credentials or secrets in source code often leaks into production if not explicitly switched to environment variables. Mocking auth for speed during development leaves massive security holes.
**Prevention:** Use `os.getenv()` for all secrets with no sensitive defaults in production code. Ensure auth mocks are strictly gated behind `FLASK_ENV=development` or similar flags, or better yet, never commit bypass code.
