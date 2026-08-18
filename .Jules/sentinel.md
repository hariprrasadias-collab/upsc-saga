## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.
## 2026-08-18 - [CRITICAL] Removed Hardcoded OPENCLAW_API_KEY Fallback
**Vulnerability:** A hardcoded fallback API key string was present in os.environ.get() for OPENCLAW_API_KEY in backend/app/services/model_manager.py.
**Learning:** Fallback values in os.environ.get() calls across this codebase may contain real hardcoded secrets previously used for local development rather than safe placeholders. This specific fallback was a hash/token string that poses a significant security risk if committed to version control.
**Prevention:** Ensure that environment variable fallbacks never contain actual credentials. Use empty strings or require the environment variable to be explicitly set. Implement automated secret scanning in the CI/CD pipeline.
