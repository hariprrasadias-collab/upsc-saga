## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2024-05-24 - Modal Dialog Accessibility
**Learning:** Custom modal components often lack semantic roles and associations, making them invisible or confusing to screen reader users. Additionally, visible text cues like `&times;` in close buttons are read aloud awkwardly if not hidden.
**Action:** Always ensure modal container elements include `role="dialog"`, `aria-modal="true"`, and an `aria-labelledby` referencing their heading ID. Close buttons should use `aria-label` and wrap visual symbols in an `aria-hidden="true"` span.
