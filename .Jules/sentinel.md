## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.

## 2026-05-03 - IDOR Vulnerability in Multiple Routes
**Vulnerability:** Several routes contained hardcoded `user_id=1` exposing IDOR vulnerabilities.
**Learning:** Avoid hardcoding user IDs and ensure parameterized queries are used consistently across all routes.
**Prevention:** Always use `get_current_user_id()` to fetch the authenticated user ID and parameterize database queries.
