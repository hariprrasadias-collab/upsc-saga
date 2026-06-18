## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.

## 2025-02-24 - Hardcoded Secrets in Source Control
**Vulnerability:** Found hardcoded OAuth client secret inside `credentials.json` and refresh token inside `token.json` committed to the repository.
**Learning:** Development credentials and state files were unintentionally committed to version control.
**Prevention:** Always add `.json` credential files to `.gitignore` and ensure environment variables are used for static secrets.
