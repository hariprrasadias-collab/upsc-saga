## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.

## 2025-02-27 - Fail Open in Admin Auth
**Vulnerability:** Found a "Fail Open" vulnerability where an exception handler in `is_admin` granted access to `user_id=1` on database failure.
**Learning:** Developers sometimes implement insecure fallbacks for local development convenience that can become critical vulnerabilities in production if they bypass security checks on system failure.
**Prevention:** Strictly enforce "Fail Secure" principles. Access control functions must return `False` (deny access) on any error or exception. Avoid hardcoded bypasses for specific user IDs.
