## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.

## 2024-03-15 - [SSRF Prevention via URL Validation]
**Vulnerability:** Several backend services (`neural_lace_service.py`, `upsc_summarizer.py`) were making direct `requests.get` calls to user-supplied URLs without validation, leading to potential Server-Side Request Forgery (SSRF) vulnerabilities where the backend could be tricked into scanning or making requests to internal network resources.
**Learning:** Python's `requests` library automatically follows redirects and accepts local/private IP addresses. A robust custom URL validator `is_safe_url` using `urllib` and `ipaddress` was needed to block loopback (e.g., 127.0.0.1) and private subnets, while exclusively allowing HTTP and HTTPS schemes.
**Prevention:** Always parse and validate user-supplied URLs before passing them to `requests.get`. Ensure the resolved hostname does not point to restricted IP ranges, and wrap the requests with strict timeouts.
