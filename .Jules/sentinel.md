## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.

## 2024-05-27 - Insecure Fail-Open Logic in Admin Auth
**Vulnerability:** The `is_admin` function caught all database exceptions and defaulted to returning `True` for User 1, intending to support development/migration. However, because the `is_admin` column was missing in the schema, this fallback triggered for ALL requests from User 1, effectively bypassing the database check and failing "open".
**Learning:** "Fail-safe" code that defaults to ALLOW access in case of error is a dangerous pattern. Dev-only backdoors (like hardcoded User 1 check) often persist into production or mask underlying configuration errors (like missing columns).
**Prevention:** Implement "Fail-Secure" logic: defaults should always be DENY. Remove dev-specific bypasses or strictly gate them behind environment flags (`if app.debug:`). Ensure schema migrations are robust so code doesn't rely on error handling for normal operation.
