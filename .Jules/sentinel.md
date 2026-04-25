## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.

## 2026-04-25 - Found IDOR Vulnerability in Autonomy Routes
**Vulnerability:** Multiple endpoints in `autonomy_routes.py` (e.g., `/settings`, `/action_log`) were hardcoding `user_id=1`, allowing any user to access or modify the primary user's data.
**Learning:** When developing locally, it is common to hardcode IDs for testing. However, leaving these in production code completely bypasses authorization checks (IDOR).
**Prevention:** Always extract the user identity from the session dynamically using `get_current_user_id()` and explicitly include ownership checks (`WHERE user_id=?`) in all queries.
