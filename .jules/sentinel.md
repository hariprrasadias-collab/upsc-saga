## 2024-05-24 - Prevent XSS in AnkiDojo Flashcards
**Vulnerability:** The AnkiDojo component rendered flashcard questions and answers using `dangerouslySetInnerHTML` without any sanitization. This allowed Cross-Site Scripting (XSS) if a user created a flashcard with malicious HTML/JavaScript content.
**Learning:** Even internal tool components that render user-generated content must sanitize HTML before injecting it into the DOM, as malicious users could exploit this vector to execute arbitrary scripts.
**Prevention:** Always use `DOMPurify.sanitize()` when dynamically rendering HTML content with `dangerouslySetInnerHTML`. Ensure `dompurify` and its types are added to project dependencies.
