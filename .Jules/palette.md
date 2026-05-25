## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-05-24 - Screen Reader Friendly Close Buttons in Modals
**Learning:** Found a pattern where '×' is used inside close buttons without ARIA labels, causing screen readers to unhelpfully announce "multiply".
**Action:** Always wrap visual '×' symbols in `<span aria-hidden="true">×</span>` and provide a descriptive `aria-label` like "Close dialog" on the parent `<button>` for all custom modals and dialogs across the app.
