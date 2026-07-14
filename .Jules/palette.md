## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-07-14 - Custom Inline Modal Accessibility Pattern
**Learning:** Custom inline modals in the application (like TemplateSelector) frequently lack standard dialog accessibility attributes (`role="dialog"`, `aria-modal="true"`) and use naked visual characters like '✕' for close buttons, which causes confusing screen reader output.
**Action:** Always apply `role="dialog"`, `aria-modal="true"`, and `aria-labelledby` to custom modals, and wrap icon-only close buttons in `<span aria-hidden="true">` with an explicit `aria-label` on the parent `<button>`.
