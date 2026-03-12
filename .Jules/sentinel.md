## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.

## 2025-03-09 - Insecure Direct Object Reference (IDOR) with Hardcoded User IDs
**Vulnerability:** Endpoints such as `/api/codex` and `/api/lore` used hardcoded `user_id=1` for all queries (e.g., `SELECT ... WHERE user_id=1`). Any user could view or modify data belonging to user ID 1 without appropriate authorization checks.
**Learning:** Relying on hardcoded or client-supplied IDs without verifying session authorization leads to critical IDOR vulnerabilities. This pattern appeared in multiple blueprints where data ownership wasn't enforced.
**Prevention:** Always extract the current user's identity dynamically from a secure session (e.g., `session.get('user_id')`) and include an explicit authorization check (`WHERE id=? AND user_id=?`) before allowing any updates or deletions of user-owned resources.
