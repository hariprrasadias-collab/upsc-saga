## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.
## 2024-04-08 - Fix XSS in AnkiDojo Flashcards
**Vulnerability:** Found un-sanitized HTML rendering via `dangerouslySetInnerHTML` for AnkiDojo flashcard questions and answers in `frontend/src/components/AnkiDojo/AnkiDojo.tsx`.
**Learning:** Raw flashcard content often originates from external sources or user input and was being directly rendered to the DOM without sanitization, exposing the app to Cross-Site Scripting (XSS) attacks.
**Prevention:** Always use a reputable library like `dompurify` (`DOMPurify.sanitize()`) when rendering raw HTML content via React's `dangerouslySetInnerHTML`. Ensure that both `dompurify` and its types (`@types/dompurify`) are properly added as dependencies to the frontend package.
