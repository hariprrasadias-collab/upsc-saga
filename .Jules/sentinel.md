## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.
## 2025-02-28 - Hardcoded IDs in Routes (IDOR Risk)
**Vulnerability:** Found hardcoded `user_id=1` in `autonomy_routes.py` method calls, creating an IDOR vulnerability where any request acts on the hardcoded user.
**Learning:** It's easy for developers to leave test/debug IDs in API calls during rapid prototyping, bypassing actual session checks.
**Prevention:** Ensure routes retrieve user context dynamically from session utilities like `get_current_user_id()` instead of passing static numbers.
