## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.
## 2024-05-24 - Fix IDOR in lore.py by replacing hardcoded user_id=1
**Vulnerability:** Insecure Direct Object Reference (IDOR) due to hardcoded user_id=1 and missing user ownership checks in PUT/DELETE routes in backend/app/routes/lore.py.
**Learning:** Hardcoding user IDs for testing endpoints can easily be forgotten and lead to cross-user data manipulation vulnerabilities.
**Prevention:** Always use `get_current_user_id()` or equivalent and ensure update/delete operations contain `AND user_id=?` authorization checks.
