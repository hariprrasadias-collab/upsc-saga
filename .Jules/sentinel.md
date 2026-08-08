## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.
## 2024-08-08 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability in `current_affairs.py` where a `limit` and `offset` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not parameterized. Developers often overlook these believing they will always be numbers and that type casting is enough security.
**Prevention:** Always use parameterized queries (`LIMIT ?`, `OFFSET ?`) even for standard SQL clauses. Never trust input types from JSON.
