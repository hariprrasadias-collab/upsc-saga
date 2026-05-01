## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.

## 2024-05-24 - Residual Hardcoded user_id in Codex API Route
**Vulnerability:** The `/api/codex/progress` and `/api/codex/update` endpoints contained a residual hardcoded `user_id=1` reference instead of dynamically fetching the authenticated user's ID.
**Learning:** Hardcoded user IDs left over from initial development create Insecure Direct Object Reference (IDOR) vulnerabilities, potentially allowing unauthenticated or incorrect access to user data.
**Prevention:** Always use `get_current_user_id()` from `app.utils.session` to fetch the contextual user and ensure all database queries enforce this authorization check via parameterization.
