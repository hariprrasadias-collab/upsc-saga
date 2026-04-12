## 2026-04-12 - Fix IDOR in Codex Routes
**Vulnerability:** The `/api/codex/progress` and `/api/codex/update` endpoints had hardcoded `user_id=1` in their SQL queries, leading to Insecure Direct Object Reference (IDOR).
**Learning:** This allowed any user to view or modify the progress of user ID 1.
**Prevention:** Use `get_current_user_id()` to dynamically fetch the authenticated user's ID and use parameterized queries (`?`) in SQL to enforce proper ownership checks.
