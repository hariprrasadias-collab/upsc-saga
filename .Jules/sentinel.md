## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.
## 2024-06-12 - Residual Hardcoded User IDs (IDOR)
**Vulnerability:** Several backend routes (e.g., `backend/app/routes/lore.py`, `codex.py`, `autonomy_routes.py`) contained residual hardcoded `user_id=1` values in their database queries and lacked ownership checks on mutations (`PUT`/`DELETE`), leading to Insecure Direct Object Reference (IDOR) / Broken Access Control vulnerabilities.
**Learning:** This is a persistent pattern across multiple endpoints in the codebase likely resulting from an incomplete transition from a single-user prototype to a multi-user authentication system.
**Prevention:** Consistently use `get_current_user_id()` from `app.utils.session` for all user-specific data retrieval. Ensure all data mutations include the `user_id` in their `WHERE` clauses to verify object ownership before execution.
