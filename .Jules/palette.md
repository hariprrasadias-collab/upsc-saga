## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-05-24 - Custom Modal Dialog Accessibility
**Learning:** Custom modal dialogs must use `role="dialog"` and `aria-modal="true"`. Furthermore, they must have an accessible name using `aria-labelledby` referencing the dialog's heading to be properly announced by screen readers. Visible text cues like `&times;` in close buttons should be wrapped in an `aria-hidden="true"` span to prevent confusing screen reader announcements.
**Action:** Always test custom modals with screen reader constraints in mind, linking titles with container `aria-labelledby` attributes and hiding decorative characters.
