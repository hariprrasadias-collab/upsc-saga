## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2025-02-14 - Close Button Accessibility
**Learning:** Close buttons with visual '×' symbols are often misread by screen readers as "multiply", which is confusing for accessibility users.
**Action:** Always wrap visual '×' symbols in `<span aria-hidden="true">×</span>` and add an `aria-label="Close dialog"` to the parent `<button>`.
