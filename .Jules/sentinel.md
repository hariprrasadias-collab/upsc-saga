## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.

## 2024-05-18 - [Fix SSRF vulnerability using safe_get]
**Vulnerability:** User-supplied URLs passed directly to `requests.get` without checking if the target is a private, loopback, or reserved IP address. Also, standard validation could be bypassed with redirects.
**Learning:** Checking the URL scheme and resolving the IP is important before making a request (`is_safe_url`), but `requests` library will automatically follow redirects. Attackers could supply a safe external URL that redirects to a sensitive internal address (e.g., `http://169.254.169.254`).
**Prevention:** Disable automatic redirects (`allow_redirects=False`) and manually check the `Location` header in redirects against the `is_safe_url` function. Implemented a `safe_get` function to enforce this policy centrally.
