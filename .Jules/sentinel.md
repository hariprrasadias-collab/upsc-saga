## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.

## 2025-02-20 - Ineffective Rate Limiting & Memory Leak
**Vulnerability:** Rate limiting relied on `request.remote_addr` which blocks the load balancer instead of the user in production, and the in-memory dictionary grew indefinitely (DoS risk).
**Learning:** In-memory rate limiting without cleanup logic is a ticking time bomb for memory leaks. Also, `remote_addr` is misleading behind proxies.
**Prevention:** Use `X-Forwarded-For` with a fallback, and implement periodic cleanup for in-memory stores.
