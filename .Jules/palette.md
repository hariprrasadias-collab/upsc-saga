## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2024-07-11 - Modal Accessibility Patterns
**Learning:** Modals require precise ARIA bindings to be screen-reader friendly. Using React's `useId` is a robust way to link `aria-labelledby` to the modal title. Additionally, icon-only close buttons (like '×') must hide their visual characters with `aria-hidden="true"` while relying on the parent button's `aria-label` to prevent screen readers from reading confusing punctuation.
**Action:** Always apply `role="dialog"`, `aria-modal="true"`, and a linked `aria-labelledby` to custom modal containers. Wrap raw close characters in `<span aria-hidden="true">`.
