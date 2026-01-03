## 2024-05-23 - [Fixed Admin Fail-Open Vulnerability]
**Vulnerability:** The `is_admin` check in `backend/app/routes/admin.py` contained a fail-open logic where it would return `True` for `user_id == 1` if a database exception occurred. This was intended as a dev/migration fallback but posed a critical security risk in production, potentially granting admin access if the database was unavailable or manipulated to error out.
**Learning:** "Fail Safe" mechanisms intended for development (like assuming user 1 is admin if DB is down) can easily become "Fail Open" vulnerabilities in production. Security logic should always "Fail Closed" (deny access on error).
**Prevention:**
1. Never assume default permissions on system failure.
2. Remove dev-only backdoors from production code paths.
3. Ensure exception handlers in auth checks return `False` or deny access.
