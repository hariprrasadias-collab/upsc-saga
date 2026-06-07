## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2024-06-06 - Modal Accessibility
**Learning:** Custom modal dialogs must have `role="dialog"`, `aria-modal="true"`, and `aria-labelledby` linking to their title. Visual cues like `&times;` inside close buttons should be wrapped in `<span aria-hidden="true">` to prevent screen readers from reading them confusingly.
**Action:** When building modals, always link the dialog role to its heading and hide purely visual icons from screen readers.
