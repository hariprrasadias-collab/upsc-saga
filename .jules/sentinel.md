## 2024-05-24 - [XSS vulnerability in AnkiDojo]
**Vulnerability:** XSS vulnerability through unsanitized user input in frontend/src/components/AnkiDojo/AnkiDojo.tsx
**Learning:** `dangerouslySetInnerHTML` is used to render question and answer texts directly without any sanitization.
**Prevention:** Always use `DOMPurify.sanitize()` before passing HTML content to `dangerouslySetInnerHTML`.
