## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2026-01-20 - Semantic Accordion Headers
**Learning:** Clickable section headers (like in Syllabus Tracker) implemented as `div`s with `onClick` handlers are invisible to keyboard users and lack semantic meaning for screen readers.
**Action:** Always replace interactive section headers with `button` elements wrapped in heading tags (e.g., `<h2><button>...</button></h2>`) and use `aria-expanded` to communicate state.
