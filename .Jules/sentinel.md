## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.
## 2024-05-14 - Hardcoded Secret in OpenClaw Fallback
**Vulnerability:** A hardcoded API key (`d25c...`) was used as the default value in `os.environ.get()` for `OPENCLAW_API_KEY`.
**Learning:** Fallback values in `os.environ.get()` calls across the codebase may contain real hardcoded secrets previously used for local development rather than safe placeholders.
**Prevention:** Always use empty strings or safe placeholders for API key defaults, and rely on environment variables exclusively.
