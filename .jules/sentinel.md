## 2025-03-01 - Fix IDOR via hardcoded user_id
**Vulnerability:** Insecure Direct Object Reference (IDOR) and Authorization Bypass. Endpoints in `codex.py` and `lore.py` were using a hardcoded `user_id=1` or completely missing `user_id` ownership checks in `UPDATE` and `DELETE` queries.
**Learning:** Hardcoding user IDs allows any user to act as the administrative or default user. Omitting ownership checks (`WHERE id=? AND user_id=?`) on modifying endpoints allows users to guess resource IDs and arbitrarily modify or delete other users' resources.
**Prevention:** Always dynamically fetch the current user's ID via `get_current_user_id()` and include explicit ownership checks (`AND user_id=?`) in all database queries that read or modify user-specific resources.
