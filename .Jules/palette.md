## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2026-08-06 - Accessible Emojis in Icon-Only Buttons
**Learning:** Emojis and symbols in buttons can be redundantly read by screen readers if they are visual-only. When making UX improvements to icon-only buttons with `aria-label`, the inner visual element (e.g., emojis) must be wrapped in `<span aria-hidden="true">`.
**Action:** Always wrap decorative icons or emojis inside buttons with `<span aria-hidden="true">`, particularly when paired with an `aria-label`, to ensure clean and semantic screen reader feedback.
