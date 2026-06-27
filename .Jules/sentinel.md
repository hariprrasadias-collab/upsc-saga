## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.

## 2025-02-27 - [Migrate Hardcoded OAuth Credentials to Environment Variables]
**Vulnerability:** Found hardcoded Google OAuth client ID and client secret inside `backend/credentials.json` mapped in `backend/app/routes/warmap.py`.
**Learning:** Checking in secret variables or credentials file directly into the codebase can leak secrets. This could result in unauthorized users creating calendar items on other user's calendars, or stealing personal user information on calendars.
**Prevention:** Avoid checking in OAuth credentials by switching to an environment-variable based configuration and falling back to a `credentials.json` which should be added to `.gitignore`.
