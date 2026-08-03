## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.
## 2025-02-28 - Cross-Site Scripting (XSS) in AnkiDojo
**Vulnerability:** The AnkiDojo component was directly passing `currentCard.question` and `currentCard.answer` into React's `dangerouslySetInnerHTML` without prior sanitization.
**Learning:** Even if data originates from an internal backend or LLM-generated flashcards, it should never be implicitly trusted on the frontend when rendering raw HTML.
**Prevention:** Always use `DOMPurify.sanitize()` before passing any dynamic string to `dangerouslySetInnerHTML` to prevent the execution of malicious scripts.
