## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.
## 2024-06-22 - Fix Hardcoded Google OAuth Credentials
**Vulnerability:** Hardcoded Google OAuth client ID and secret in `backend/credentials.json` which was committed to source control.
**Learning:** Checking in static configuration files containing sensitive credentials exposes them to anyone with repository access. Environment variables should be used for secrets.
**Prevention:** Always load sensitive credentials dynamically from environment variables and ensure files containing them are added to `.gitignore`.
