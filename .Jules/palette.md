## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2025-02-28 - Emoji Icon Buttons Accessibility in Data Tables
**Learning:** Icon-only buttons using emojis in data tables (like edit/delete actions) are frequently read by screen readers as the default emoji description repeatedly, causing a poor UX and navigation experience.
**Action:** Always add an `aria-label` to the button and wrap the emoji itself in a `<span aria-hidden="true">` to override the default text and ensure the screen reader announces a clean, actionable label. Tooltips (`title`) are also highly recommended for sighted users.
