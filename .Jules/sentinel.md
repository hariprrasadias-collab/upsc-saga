## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.
## $(date +%Y-%m-%d) - Fix Hardcoded OpenClaw API Key
**Vulnerability:** Found a hardcoded API key for OpenClaw in the os.environ.get fallback value.
**Learning:** Default fallback values in os.environ.get() calls across the codebase may contain real hardcoded secrets previously used for local development rather than safe placeholders.
**Prevention:** Always verify that fallback values for environment variables do not contain sensitive credentials.
