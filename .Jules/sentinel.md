## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.
## 2026-08-04 - SQL Injection in Dynamic Limits via f-string
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string using f-strings (`query += f' LIMIT {int(filters["limit"])}'`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. While casting to `int` provides some protection, it is an anti-pattern. Developers often overlook these believing they will always be numbers, or because the query builder does not explicitly support LIMIT.
**Prevention:** Always cast numeric inputs to their respective types (int/float) AND use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.
