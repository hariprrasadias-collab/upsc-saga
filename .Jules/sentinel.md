## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.

## 2024-05-24 - Hardcoded Secret in Fallback Config
**Vulnerability:** A hardcoded OpenClaw API key was used as a fallback default in `os.environ.get()`.
**Learning:** Default values in environment variable lookups can easily become forgotten hardcoded secrets, bypassing configuration management.
**Prevention:** Never provide a hardcoded secret string as the fallback for `os.environ.get()`. Ensure configuration gracefully degrades or fails securely if a required secret is missing.
