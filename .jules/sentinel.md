## 2025-05-18 - XSS Vulnerability in Flashcards
**Vulnerability:** XSS vulnerability in AnkiDojo where raw HTML was rendered via dangerouslySetInnerHTML without sanitization.
**Learning:** Even internal tool data should be sanitized before rendering as HTML to prevent stored XSS attacks if data sources are compromised.
**Prevention:** Always use a sanitization library like DOMPurify when using dangerouslySetInnerHTML.
