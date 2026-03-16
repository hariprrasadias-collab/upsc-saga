## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.
## 2024-05-25 - SSRF Prevention via URL Validation
**Vulnerability:** Found multiple instances of `requests.get()` fetching user-provided URLs without validation (SSRF risk) in `neural_lace_service.py` and `upsc_summarizer.py`.
**Learning:** Pre-flight URL validation using `socket.gethostbyname()` and `ipaddress` provides a first line of defense against SSRF, but has limitations like DNS rebinding, HTTP redirects bypassing the check, and IPv6 resolution issues (`socket.getaddrinfo` is better).
**Prevention:** Always use a utility like `is_safe_url` to block loopback, private, reserved, multicast, and unspecified IPs before making outbound HTTP requests. For robust protection, consider using a custom transport adapter to validate IPs during the connection phase, or disable redirects (`allow_redirects=False`) and manually validate the `Location` header.
## 2024-05-25 - Fix duplicate NPM build scripts
**Vulnerability:** A duplicate `"scripts"` block in `package.json` silently overwrites the previous definition, causing deployment scripts to fail (e.g. `Publish directory dist does not exist!`).
**Learning:** JSON parsers typically use the last-defined key when duplicates exist. Always ensure `package.json` keys are unique and use the correct package manager (`pnpm` vs `npm`) as defined in the deployment environment.
**Prevention:** Regularly validate `package.json` syntax and structure. Test build scripts locally using the exact environment configuration (`NODE_ENV=production pnpm run build`) before pushing to deployment platforms.
