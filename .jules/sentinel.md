## 2025-06-08 - XSS in Flashcards
**Vulnerability:** Found unescaped user-generated content rendered using dangerouslySetInnerHTML in the AnkiDojo flashcards feature.
**Learning:** Flashcard questions/answers generated via AI or user inputs must always be treated as untrusted data before rendering as raw HTML in React components.
**Prevention:** Always wrap dynamically generated HTML strings passed to dangerouslySetInnerHTML with DOMPurify.sanitize() to prevent XSS payloads.
