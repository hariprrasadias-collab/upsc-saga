## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.
## 2025-06-11 - Exposed Google OAuth Secrets
**Vulnerability:** Found credentials.json and token.json checked into the repository containing Google OAuth client_secret, access tokens, and refresh tokens.
**Learning:** Even if files are in .gitignore, they can be mistakenly added and tracked by git. Double check git status when dealing with OAuth flows.
**Prevention:** Use git rm --cached to remove mistakenly tracked files and rely on environment variables for API keys in the future.
