## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.

## 2024-09-12 - Hardcoded API Key in Fallback Logic
**Vulnerability:** A hardcoded OpenClaw API key was discovered as a default fallback parameter in `os.environ.get()` within the ModelManager configuration.
**Learning:** Hardcoded credentials can easily slip into codebase as default fallback values intended for local development convenience. They expose sensitive tokens if the repo is made public.
**Prevention:** Never provide fallback strings for secrets. Applications should fail gracefully or require manual environment setup when secrets are missing.
