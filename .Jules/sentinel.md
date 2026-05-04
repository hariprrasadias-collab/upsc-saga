## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.

## 2026-05-04 - Hardcoded user ID leads to IDOR vulnerability
**Vulnerability:** The 'user_id' was hardcoded to '1' directly into database queries in the '/api/timebox' endpoints (e.g., 'WHERE user_id = 1'), causing an Insecure Direct Object Reference (IDOR) vulnerability that bypassed user authorization.
**Learning:** Hardcoding user identifiers in SQL queries creates significant security vulnerabilities by allowing any user to access or modify data belonging to the hardcoded ID. Queries must always use parameterized authentication tokens to securely verify identity context.
**Prevention:** Always dynamically fetch the authenticated user's ID via the session context (e.g., 'get_current_user_id()') and use parameterized queries (e.g., 'WHERE user_id = ?') to prevent unauthorized data access or modification.
