## 2026-10-04 - [XSS Protection in React]
**Vulnerability:** Direct interpolation of user data into dangerouslySetInnerHTML in AnkiDojo component.
**Learning:** The frontend used dangerouslySetInnerHTML without sanitizing the Anki flashcard data, leading to a Cross-Site Scripting (XSS) vulnerability if malicious data were present.
**Prevention:** Never trust user input. Always use DOMPurify.sanitize() when using dangerouslySetInnerHTML.
