## 2024-05-19 - [Fix XSS in AnkiDojo]
**Vulnerability:** XSS vulnerability in `AnkiDojo.tsx` where Anki card questions and answers were rendered using `dangerouslySetInnerHTML` without sanitizing the input.
**Learning:** `dangerouslySetInnerHTML` should never be used with user-provided or external data without sanitizing it first.
**Prevention:** Always use `DOMPurify.sanitize()` or a similar library to sanitize HTML input before passing it to `dangerouslySetInnerHTML`.
