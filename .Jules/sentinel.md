## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.
## 2026-08-17 - Remove hardcoded API keys and credentials
**Vulnerability:** Google OAuth credentials and a fallback API key for OpenClaw were hardcoded or checked into the repository as plaintext.
**Learning:** Hardcoded credentials or checking in `credentials.json` and `token.json` poses a critical risk of unauthorized access. Fallback secrets must not be stored in source code.
**Prevention:** Ensure `credentials.json` and `token.json` are added to `.gitignore` and use strictly environment variables without hardcoded fallback values for all secrets.
