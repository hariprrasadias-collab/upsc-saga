## 2024-05-18 - Improve accessibility of close buttons
**Learning:** Found multiple close buttons (e.g., `×`, `✕`) in modal components lacking `aria-label`. Without this, screen readers just read "button", making it difficult for visually impaired users to know how to dismiss a modal.
**Action:** Always include `aria-label="Close"` on modal close buttons that only use an icon or text symbol like "×".
