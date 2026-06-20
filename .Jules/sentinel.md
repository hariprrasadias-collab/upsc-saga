## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.
## 2024-06-19 - Hardcoded API Credentials
**Vulnerability:** Found hardcoded `credentials.json` and `token.json` files committed to the repository, containing OAuth secrets.
**Learning:** Always keep static secrets out of source control. Dynamic state files like `token.json` should also be ignored but preserved locally.
**Prevention:** Use environment variables for API keys and secrets, and ensure sensitive local files are strictly covered by `.gitignore`.
