## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2024-05-24 - Modal Close Button Accessibility
**Learning:** Close buttons using a visual '×' symbol cause screen readers to announce 'multiply', confusing users.
**Action:** Always wrap the visual '×' in `<span aria-hidden="true">×</span>` and apply a descriptive `aria-label` to the parent `<button>` element.
