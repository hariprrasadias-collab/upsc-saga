## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.
## 2025-05-16 - Prevent XSS in User Content Rendering
**Vulnerability:** Found `dangerouslySetInnerHTML` rendering unsanitized `currentCard.question` and `currentCard.answer` directly from API payload.
**Learning:** React's `dangerouslySetInnerHTML` is commonly used to render formatted flashcard content, but it inherently trusts the provided HTML. If user-generated or third-party content (like imported Anki decks) contains malicious scripts, it creates a direct XSS vector.
**Prevention:** Always use `DOMPurify.sanitize()` (or a similar sanitization library) to wrap any string before passing it to `dangerouslySetInnerHTML`, ensuring that malicious script tags or attributes are stripped out while preserving the legitimate HTML structure.
