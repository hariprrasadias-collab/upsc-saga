## 2026-04-02 - [Stored XSS in Anki Dojo Flashcards]
**Vulnerability:** Raw flashcard data mapped directly to dangerouslySetInnerHTML in React component without sanitization.
**Learning:** Content considered "internal" or imported from external decks (like Anki questions/answers) is often implicitly trusted by developers but can serve as a vector for stored XSS if it contains malicious script tags or handlers.
**Prevention:** Always enforce strict sanitization using established libraries like DOMPurify before injecting dynamic content into dangerouslySetInnerHTML, even for assumed-safe internal text.
