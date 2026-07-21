## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
## 2026-07-21 - Icon-only buttons accessibility
**Learning:** Screen readers read out confusing characters for symbol-only buttons without proper aria attributes (e.g. reading '×' as 'times' or 'multiply').
**Action:** Always wrap visual icon-only symbols in a <span aria-hidden="true"> and add a descriptive aria-label to the parent <button>.
