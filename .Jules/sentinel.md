## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.
## 2026-03-28 - [XSS Vulnerability in Anki Flashcards]
**Vulnerability:** XSS vulnerability through direct injection of unsanitized HTML in `dangerouslySetInnerHTML` for flashcard content.
**Learning:** The frontend uses `dangerouslySetInnerHTML` to render flashcard questions and answers. Direct assignment of unvalidated and unsanitized HTML is vulnerable to Cross-Site Scripting (XSS).
**Prevention:** Always sanitize any untrusted or rich text HTML input with `DOMPurify.sanitize()` before passing it to `dangerouslySetInnerHTML`. Ensure `dompurify` and its types are strictly declared in `frontend/package.json`.
