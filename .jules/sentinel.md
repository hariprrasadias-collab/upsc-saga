## 2024-05-18 - Fix XSS Vulnerability in AnkiDojo component
**Vulnerability:** User-supplied Anki card content (questions and answers) was rendered directly using Reacts `dangerouslySetInnerHTML` without proper HTML sanitization in `frontend/src/components/AnkiDojo/AnkiDojo.tsx`.
**Learning:** Reacts `dangerouslySetInnerHTML` is dangerous by design and any user-controlled inputs passed to it must be explicitly sanitized, especially for rich-text contents like Anki cards where arbitrary HTML might be rendered.
**Prevention:** Always use a reputable sanitizer library like `DOMPurify` to clean user-generated HTML content before passing it to `dangerouslySetInnerHTML`.
