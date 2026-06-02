## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-05-23 - Modal Close Button Accessibility
**Learning:** Icon-only close buttons using visual characters like '×' are announced by screen readers as "multiply", which is confusing. Wrapping the visual character in an `aria-hidden="true"` span and adding a descriptive `aria-label` to the parent `<button>` makes the purpose clear to all users.
**Action:** Always wrap visual close icons (like '×') with `aria-hidden="true"` and apply `aria-label` on the parent `<button>` across all custom modals and dialogs.
