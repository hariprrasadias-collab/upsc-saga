## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.

## $(date +%Y-%m-%d) - Fix IDOR in timebox routes
**Vulnerability:** IDOR (Insecure Direct Object Reference) / Authentication Bypass where `backend/app/routes/timebox.py` hardcoded `user_id = 1` across all endpoints (`get`, `add`, `delete`, `suggestions`), allowing any user to edit/view user 1's data instead of their own.
**Learning:** Some backend routes rely on a hardcoded user ID (`user_id = 1`) as a placeholder from early development instead of verifying the authenticated user.
**Prevention:** Always use `get_current_user_id()` from `app.utils.session` for user identification and parameterized queries (`WHERE user_id = ?`) to secure all database operations. Do not hardcode user IDs.
