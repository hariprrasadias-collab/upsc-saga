
## 2026-04-03 - Fix Insecure Direct Object Reference (IDOR) in Lore Tablets
**Vulnerability:** The `/api/lore` and `/api/lore/<nid>` endpoints allowed unauthorized access, updates, and deletions of any user's lore tablets due to hardcoded `user_id=1` and missing ownership checks (`WHERE user_id=?`) in `PUT` and `DELETE` actions.
**Learning:** Hardcoding identifiers like `user_id=1` during development often leads to serious IDOR vulnerabilities in production if not properly refactored to use dynamic session data.
**Prevention:** Always extract the user ID dynamically using `get_current_user_id()` from `app.utils.session` and explicitly include ownership checks (`AND user_id=?`) in all database queries to prevent unauthorized access to restricted resources.
