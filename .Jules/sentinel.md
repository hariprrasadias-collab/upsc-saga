## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.

## 2024-06-19 - Proxy-Aware Rate Limiting and Wildcard Injection
**Vulnerability:**
1. Rate limiting used `request.remote_addr`, which returns the Load Balancer's IP in production (Render), causing all users to share a single rate limit (DoS risk for users).
2. SQL `LIKE` queries allowed wildcard injection (`%` and `_`), enabling potential Denial of Service via expensive pattern matching (e.g., `%%%%%%%%`).
**Learning:**
1. In cloud environments, `remote_addr` is rarely the client IP. Trusting it for security/logic can lead to global lockouts.
2. `LIKE` operators in SQL are not automatically safe even with parameterized queries if the *content* of the parameter contains wildcards.
**Prevention:**
1. Use `X-Forwarded-For` header parsing to identify real clients behind proxies.
2. Explicitly escape special characters in `LIKE` inputs and use the `ESCAPE '\'` clause in SQL.
