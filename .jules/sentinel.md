## 2024-05-08 - XSS in AnkiDojo
**Vulnerability:** XSS vulnerability through unsanitized user content loaded via API in `frontend/src/components/AnkiDojo/AnkiDojo.tsx` using `dangerouslySetInnerHTML`.
**Learning:** React`s `dangerouslySetInnerHTML` is often necessary to render rich text like Anki cards, but if the content originates from an untrusted source or an API serving user-generated content, it must be explicitly sanitized.
**Prevention:** Always sanitize dynamically loaded HTML using a robust library like `DOMPurify` before rendering it with `dangerouslySetInnerHTML`.
