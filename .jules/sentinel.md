
## 2024-05-27 - Hardcoded User ID in Timebox Endpoints
**Vulnerability:** IDOR (Insecure Direct Object Reference). The `timebox.py` route hardcoded `user_id = 1` in its endpoints. Any user interacting with the endpoints would be modifying and viewing the records of User 1.
**Learning:** Hardcoded identities in routes bypass authorization checks entirely, resulting in unauthorized data access or modification. Always use context-aware utilities to ascertain identity.
**Prevention:** Always extract identity dynamically using session context functions (like `get_current_user_id()`) and parameterize queries filtering by `user_id`. Avoid hardcoding identity testing defaults in production paths.
