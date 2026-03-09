## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.
## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a potential SQL injection vulnerability where `limit` and `offset` parameters were directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`), albeit with an `int()` cast.
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not parameterized, and relying on `int()` casting inside f-strings is a bad practice that makes code fragile to future modifications.
**Prevention:** Always use parameterized queries (e.g., `LIMIT ? OFFSET ?`) for all user-provided variables, including numbers, to enforce strong defense in depth.
