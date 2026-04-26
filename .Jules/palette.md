## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2026-04-26 - Modal Close Button Accessibility
**Learning:** Icon-only close buttons in modals (like '×') can be read incorrectly by screen readers (e.g., 'multiply' or 'times') or missed completely if they lack proper labeling and markup.
**Action:** Always wrap symbol-based icons in `<span aria-hidden="true">`, and provide a descriptive `aria-label` on the parent `<button>` to ensure the action is clear to assistive technologies.
