## 2025-02-21 - Authorization Bypass in Admin Route
**Vulnerability:** A fail-safe in `backend/app/routes/admin.py` granted admin privileges to user ID 1 in the event of any database or runtime exception (e.g., missing column).
**Learning:** Hardcoded fallbacks meant to preserve access during development or migration can become critical vulnerabilities in production if error conditions can be forced or simulated by attackers.
**Prevention:** Always implement fail-secure logic. Authentication and authorization checks must strictly return `False` or deny access on any error state, never defaulting to granting privileges.
