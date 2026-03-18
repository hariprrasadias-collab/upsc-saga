## 2024-05-18 - [Fix Insecure Direct Object Reference (IDOR) in mock_tests]
**Vulnerability:** The mock_tests.py API endpoints (`save_answer`, `submit_attempt`, `get_attempt_results`) failed to verify that the attempt ID belongs to the authenticated user, allowing an attacker to submit answers or retrieve results for any other user. Also `start_test` hardcoded the `user_id` to 1.
**Learning:** Hardcoded IDs and missing ownership checks are prevalent when test data or basic prototyping is used. We must ensure robust IDOR checks before calling `conn.execute(...)`.
**Prevention:** Always extract the user ID dynamically using `session.get('user_id') or 1` and append a `WHERE user_id = ?` clause or explicitly fetch and compare `attempt['user_id'] != user_id`.
