## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-05-24 - Icon-only button Accessibility
**Learning:** When using emojis or symbols as the sole content of a button, screen readers may read the literal character name along with the `aria-label`, causing redundant or confusing output.
**Action:** Always wrap the inner visual element of an icon-only button in `<span aria-hidden="true">` when an `aria-label` is provided on the button.
