## 2025-03-03 - XSS Vulnerability in AnkiDojo
**Vulnerability:** User-generated Anki card content (questions and answers) was being rendered directly into the DOM using React's `dangerouslySetInnerHTML` without any prior sanitization.
**Learning:** This is a classic Cross-Site Scripting (XSS) vulnerability. If a malicious user were to inject a script tag into an Anki card, it would be executed when rendered.
**Prevention:** Always sanitize user-generated content before rendering it as HTML. In React, use a library like `DOMPurify` to clean the HTML string before passing it to `dangerouslySetInnerHTML`.
