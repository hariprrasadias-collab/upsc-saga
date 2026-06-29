## 2026-06-28 - XSS in AnkiDojo via dangerouslySetInnerHTML
**Vulnerability:** The AnkiDojo component used `dangerouslySetInnerHTML` to render un-sanitized flashcard questions and answers, exposing the application to Cross-Site Scripting (XSS).
**Learning:** Even internal or trusted data sources (like flashcards) should be sanitized if rendered as raw HTML, as malicious payloads could be injected through the data ingestion pipeline or API manipulation. The risk is compounded by the fact that `dangerouslySetInnerHTML` executes scripts.
**Prevention:** Always use a robust HTML sanitization library like `dompurify` (e.g., `DOMPurify.sanitize(input)`) before passing data to `dangerouslySetInnerHTML`.
