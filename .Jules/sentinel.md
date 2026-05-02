## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.
## 2024-05-24 - XSS in dangerouslySetInnerHTML
**Vulnerability:** Found an XSS vulnerability in `frontend/src/components/AnkiDojo/AnkiDojo.tsx` where user-controlled strings (flashcard text) were passed to `dangerouslySetInnerHTML` without sanitization.
**Learning:** Always use a library like `DOMPurify` to sanitize HTML content before rendering it via `dangerouslySetInnerHTML`.
**Prevention:** Sanitize inputs before rendering dynamically generated HTML.
