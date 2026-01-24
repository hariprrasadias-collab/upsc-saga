## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.

## 2025-02-14 - Stored XSS in Anki Integration
**Vulnerability:** Raw HTML content from the Anki Connect API was being rendered using `dangerouslySetInnerHTML` without sanitization in the `AnkiDojo` component.
**Learning:** External data sources (even local ones like Anki Connect) must be treated as untrusted, especially when handling rich text/HTML content.
**Prevention:** Implemented `sanitizeHtml` utility using `DOMParser` to strip scripts and unsafe attributes before rendering.
