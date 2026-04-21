## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.

## 2026-04-21 - Parameterize Limit and Offset clauses
**Vulnerability:** Found a potential SQL injection weakness where a `limit` parameter from JSON input was directly interpolated into a SQL query string even with an int conversion (`query += f' LIMIT {int(filters["limit"])}'`).
**Learning:** Best practice requires using parameterized queries even for integer limit and offset parameters to ensure defense-in-depth.
**Prevention:** Use parameterized queries (`LIMIT ? OFFSET ?`) for standard SQL clauses instead of string concatenation.
