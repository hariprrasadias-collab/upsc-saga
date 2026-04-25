## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.
## 2025-02-28 - Hardcoded User ID in Timebox Routes
**Vulnerability:** Found multiple endpoints in `backend/app/routes/timebox.py` (`get_timeboxes`, `add_timebox`, `delete_timebox`, `get_suggestions`) using a hardcoded `user_id = 1` in SQL queries, creating an Insecure Direct Object Reference (IDOR) vulnerability.
**Learning:** Hardcoding `user_id = 1` bypasses proper session authentication, allowing any request to read, modify, or delete data belonging to the first user. Subqueries mapping other tables (like `study_sessions` to `time_boxes`) also need strict `user_id = tb.user_id` correlation to ensure data isn't cross-contaminated across users.
**Prevention:** Always extract `user_id` dynamically using `get_current_user_id()` from `app.utils.session` and explicitly use it as a parameter in all SQL queries (`WHERE user_id = ?`). Ensure all subqueries within endpoints correlate user IDs securely.
