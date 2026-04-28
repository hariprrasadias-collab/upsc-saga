## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.
## 2025-02-20 - IDOR in Timebox Routes
**Vulnerability:** Found multiple Insecure Direct Object Reference (IDOR) vulnerabilities where the hardcoded `user_id = 1` was being used in SQL queries across `backend/app/routes/timebox.py` endpoints (like get, add, and delete).
**Learning:** Even if `user_id` is intended to be dynamically fetched or is mocked for development, leaving hardcoded user IDs in routes bypassing `get_current_user_id()` creates a serious missing authorization vulnerability that could allow any user to act on behalf of the hardcoded ID.
**Prevention:** Ensure all authenticated endpoints utilize a session management utility like `get_current_user_id()` to securely identify the caller, and use parameterized queries when passing that ID to database access functions.
