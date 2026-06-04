## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.
## 2026-06-04 - Remove hardcoded OpenClaw API Key
**Vulnerability:** Hardcoded API key for OpenClaw found as a fallback in `os.environ.get`.
**Learning:** Hardcoding credentials as fallbacks exposes them to version control, undermining environment variable protections.
**Prevention:** Always rely strictly on environment variables for sensitive credentials, ensuring no fallback values are hardcoded in the source code.
