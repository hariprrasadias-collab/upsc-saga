## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.

## 2026-05-30 - SQL Injection in Current Affairs Dynamic Limits

**Vulnerability:** Found a SQL injection vulnerability where `limit` and `offset` parameters from a JSON request were directly interpolated into a SQL query string via f-strings (`query += f' LIMIT {int(filters["limit"])}'`) in `backend/app/db_models/current_affairs.py`.
**Learning:** Even though the inputs were cast using `int()`, preventing direct malicious string injection, using string interpolation for SQL queries violates standard security practices. Developers often assume type casting makes string concatenation safe, but parameterized queries are the only robust defense.
**Prevention:** Always use fully parameterized queries (e.g., `LIMIT ? OFFSET ?`) and append the values to the parameter list, regardless of whether the inputs have been cast to numbers. Never rely on type casting as a substitute for parameterization.
