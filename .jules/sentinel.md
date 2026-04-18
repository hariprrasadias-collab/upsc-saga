## 2024-05-24 - Hardcoded IDOR in Codex API
**Vulnerability:** The `/api/codex/progress` and `/api/codex/update` endpoints in `backend/app/routes/codex.py` contained hardcoded `user_id=1` values, allowing any authenticated user to potentially access or modify user 1's progress.
**Learning:** This is a recurring pattern in the codebase, likely a remnant of single-user MVP development. Even in internal or mock tools, user IDs must be dynamically fetched and validated to establish proper ownership boundaries.
**Prevention:** Always use `get_current_user_id()` from `app.utils.session` and enforce ownership checks with parameterized queries (`WHERE user_id=?`).
