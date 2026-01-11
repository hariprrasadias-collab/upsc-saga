## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.

## 2025-05-22 - Authorization Bypass via Fail-Open Logic
**Vulnerability:** The `is_admin` check contained a fallback mechanism that granted administrative access to a default user (ID 1) if the database query raised an exception.
**Learning:** "Fail-safe" logic in authentication often gets inverted to "Fail-Open" (granting access on failure) to aid development/debugging. Relying on exception handling to bypass security checks creates a backdoor if the system is under stress or attack.
**Prevention:** Always "Fail Closed" in security-critical functions. If a check cannot be completed (e.g., DB error), the default action must be to deny access.
