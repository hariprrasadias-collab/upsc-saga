## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.
## 2024-05-24 - [IDOR in Quiz Endpoints]
**Vulnerability:** Missing authorization checks and hardcoded `user_id = 1` in quiz session endpoints (`pyq.py`).
**Learning:** Developers relied on hardcoded dev user IDs in SQL queries which bypassed ownership verification for quiz sessions, leading to a critical Insecure Direct Object Reference vulnerability.
**Prevention:** Always extract `user_id` dynamically (e.g., via `get_current_user_id()`) and explicitly include `user_id = ?` in `WHERE` clauses for read/write queries.
