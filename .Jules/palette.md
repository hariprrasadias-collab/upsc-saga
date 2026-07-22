## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-07-21 - Icon-only buttons accessibility
**Learning:** Screen readers read out confusing characters for symbol-only buttons without proper aria attributes (e.g. reading '×' as 'times' or 'multiply').
**Action:** Always wrap visual icon-only symbols in a `<span aria-hidden="true">` and add a descriptive `aria-label` to the parent `<button>`.
