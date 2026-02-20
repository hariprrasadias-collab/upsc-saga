## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.

## 2025-05-27 - Fail-Open Authorization Logic
**Vulnerability:** The `is_admin` check defaulted to `True` (granting access) if a database error occurred, intended as a dev fallback. Combined with a hardcoded user ID of 1, this made any DB failure a privilege escalation vector.
**Learning:** "Fail-safe" mechanisms intended for development can become dangerous backdoors in production. Security checks must always "Fail Secure" (deny by default).
**Prevention:** Authorization functions must return `False`/deny in all error paths. Remove dev-only bypasses from production code paths or gate them strictly behind environment variables.
