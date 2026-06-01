## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2024-05-23 - Modal Dialog Accessibility
**Learning:** Custom modal dialogs (like popup reports) require proper ARIA attributes to be announced by screen readers correctly. When modifying generic `<div>` wrappers into modals, they must have `role="dialog"`, `aria-modal="true"`, and an `aria-labelledby` linking to a visible heading element.
**Action:** Always ensure modal overlays have these ARIA attributes and that their close buttons have hidden text (like `aria-label="Close"`) and mask the visual X with `<span aria-hidden="true">×</span>`.
