## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.

## 2024-05-25 - XSS Vulnerability in DOM Manipulation
**Vulnerability:** Found XSS vulnerability where untrusted data is rendered via `dangerouslySetInnerHTML` and `innerHTML` without sanitization.
**Learning:** `dangerouslySetInnerHTML` in React and `.innerHTML` in pure JS both allow execution of malicious scripts if data comes from untrusted sources.
**Prevention:** Always use `DOMPurify.sanitize()` to clean any untrusted HTML before rendering it directly into the DOM.
