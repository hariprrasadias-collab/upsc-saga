## 2025-02-18 - Admin Authorization Fail Open
**Vulnerability:** The `is_admin` function returned `True` (granting access) if a database exception occurred and the user ID was 1 (which is the hardcoded default).
**Learning:** Hardcoded "dev/migration" fallbacks can become critical "Fail Open" vulnerabilities in production if not strictly guarded or removed.
**Prevention:** Always implement "Fail Secure" logic: if a security check cannot complete (e.g., DB error), access must be denied (`return False`), never granted.
