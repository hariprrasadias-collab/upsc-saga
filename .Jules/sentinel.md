## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.

## 2026-03-31 - [DOMPurify for AnkiDojo XSS]
**Vulnerability:** XSS vulnerability in AnkiDojo Flashcards due to unsanitized dangerouslySetInnerHTML.
**Learning:** HTML from flashcards needs to be sanitized since the input might contain malicious tags.
**Prevention:** Always use DOMPurify.sanitize() when rendering HTML content in Anki flashcards.
