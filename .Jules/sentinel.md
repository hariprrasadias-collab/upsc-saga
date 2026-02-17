## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.

## 2026-02-17 - Hardcoded Flask SECRET_KEY
**Vulnerability:** Found a hardcoded `SECRET_KEY` in `backend/app/__init__.py` which compromises all session data if exposed.
**Learning:** `create_app` functions often include hardcoded secrets for convenience during development, which can easily be carried into production.
**Prevention:** Enforce environment variable checks at application startup. Fail securely (raise error) if critical secrets are missing in production environments.
