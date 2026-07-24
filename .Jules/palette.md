## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-07-24 - Accessible Action Buttons in Admin Dashboard
**Learning:** Found an accessibility issue pattern where tables with generic actions like Edit and Delete used plain emojis without any `aria-label`. Screen readers would announce the literal emoji character instead of the button's semantic intent, leading to confusing navigation for users depending on assistive tech.
**Action:** When adding edit/delete buttons, always use `aria-label`s to clearly communicate the action, and use `<span aria-hidden="true">` on visual icons/emojis to avoid redundant screen reader readouts.
