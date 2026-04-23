
## 2025-02-27 - Hardcoded User IDs and IDOR (Insecure Direct Object Reference)
**Vulnerability:** Found endpoints (like `/api/codex/progress` and `/api/codex/update`) utilizing a hardcoded `user_id=1` in the SQLite SQL queries rather than dynamically determining the user making the request.
**Learning:** This creates a critical IDOR (Insecure Direct Object Reference) and authentication bypass vulnerability. Any user hitting these endpoints could view and modify data belonging to user 1. We've seen this pattern spread across several modules in `backend/app/routes/`.
**Prevention:** Always use `get_current_user_id()` from `app.utils.session` to fetch the dynamic context of the authenticated user. Pass this dynamically derived ID to database execution functions using `?` parameterized queries (`WHERE user_id=?`). Do not hardcode user IDs or use f-strings for user input in SQL context.
