## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.

## 2024-04-10 - [SQL Injection Fix in current_affairs]
**Vulnerability:** A SQL Injection vulnerability existed in `backend/app/db_models/current_affairs.py` within `get_saved_articles()` where `LIMIT` and `OFFSET` clauses used string interpolation (`f' LIMIT {int(...)}'`). Although mitigated by `int()` conversion, this is insecure practice and prone to accidental bypasses if types change.
**Learning:** Even if data is cast to an integer before string interpolation, dynamically inserting values directly into SQL strings rather than using DB API parameter bindings violates defense-in-depth principles.
**Prevention:** Always use parameterized queries (e.g., `LIMIT ? OFFSET ?`) regardless of the expected type to allow the database driver to safely handle all inputs.
