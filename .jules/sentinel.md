## 2026-04-11 - Fix IDOR in Lore Routes
**Vulnerability:** Insecure Direct Object Reference (IDOR) with hardcoded user ID. The `lore.py` endpoint hardcoded `user_id=1` and lacked ownership checks on DELETE/PUT requests, allowing any user to edit/delete any lore tablet.
**Learning:** Found that `get_current_user_id()` from `app.utils.session` is the standard pattern for getting the authenticated user ID. Also noticed other endpoints (codex, predictive, autonomy, planner) likely have similar issues.
**Prevention:** Always use `get_current_user_id()` to fetch the user ID dynamically and include `AND user_id=?` in the WHERE clause for UPDATE/DELETE operations to enforce ownership boundaries.
