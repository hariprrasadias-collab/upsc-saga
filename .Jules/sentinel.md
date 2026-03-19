## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.

## 2026-03-19 - Flask Query Parameter Integer Type Casting
**Vulnerability:** Missing type=int in Flask request.args.get() for numeric parameters (like limit/offset) leading to potential SQL Injection or type confusion when passed to db queries.
**Learning:** In Flask routes, explicitly cast numeric query parameters to integers (e.g., request.args.get('limit', 20, type=int)) to prevent string-based type confusion and SQL injection vulnerabilities when parameters are passed to parameterized database queries.
**Prevention:** Always use type=int for numeric query parameters like limits and offsets.
