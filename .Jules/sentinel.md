## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.

## 2026-03-18 - SSRF via IP Parsing Nuances
**Vulnerability:** Found an SSRF vulnerability where external URLs could be fetched using `requests.get()` without fully verifying IP safety against metadata (169.254.169.254) or unspecified (0.0.0.0) IPs, nor did it verify redirects.
**Learning:** Basic loopback/private checks in Python's `ipaddress` module (`is_private`, `is_loopback`) do not catch cloud metadata IPs, which are classified as `is_link_local`, nor 0.0.0.0 (`is_unspecified`). Redirects must also be manually processed and verified.
**Prevention:** Use a robust custom request wrapper (like `safe_requests_get`) that disables automatic redirects, explicitly checks all resolved IP properties (including `is_link_local` and `is_unspecified` or `not is_global`), and validates each hop in a redirect chain.
