## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.
## 2025-03-14 - [Type Confusion / Potential SQLi in limit parameters]
**Vulnerability:** Found `request.args.get("limit", 20)` without explicit `type=int` being passed to parameterized queries in Flask routes.
**Learning:** Treating integer constraints as strings risks type confusion, SQL syntax errors, or driver-specific unexpected behaviors which could be stepping stones for exploitation.
**Prevention:** Always explicitly cast numeric query parameters like limit and offset to integers using `type=int` in Flask `request.args.get()`.
