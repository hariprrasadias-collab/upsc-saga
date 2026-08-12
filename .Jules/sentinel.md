## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.
## 2026-08-12 - [Hardcoded OPENCLAW_API_KEY]
**Vulnerability:** Found a hardcoded API key fallback value for OPENCLAW_API_KEY in backend/app/services/model_manager.py.
**Learning:** Using real secrets as fallback values in os.environ.get() exposes credentials to anyone with repository access.
**Prevention:** Always use safe, empty, or dummy placeholders (e.g., '') for default fallback values of sensitive credentials, and ensure real keys are strictly passed via environment variables.
