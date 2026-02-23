## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.

## 2026-02-03 - Hardcoded Flask Secret Key
**Vulnerability:** The Flask `SECRET_KEY` was hardcoded in `backend/app/__init__.py`, exposing session security to anyone with access to the source code.
**Learning:** Development defaults often leak into production code when they are set directly in the application factory instead of loaded via environment variables with a fallback.
**Prevention:** Use `python-dotenv` to load secrets from `.env` and `os.environ.get()` with a safe default (or no default in prod) to ensure secrets are externalized.
