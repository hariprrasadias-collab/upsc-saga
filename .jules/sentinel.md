## 2024-05-23 - [Sanitization without Bleach]
**Vulnerability:** XSS vulnerability found in AnkiDojo where `dangerouslySetInnerHTML` consumed potentially unsafe HTML from an Anki instance.
**Learning:** `bleach` was not available in the environment, and adding dependencies was restricted. I had to implement a custom whitelist-based sanitizer using Python's standard `html.parser`.
**Prevention:** Use the `WhiteListSanitizer` class in `backend/app/utils/security.py` for any future rich text sanitization needs where `bleach` is unavailable. It strictly whitelists safe tags/attributes and strips dangerous ones like `<script>` and `javascript:`.
