## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-05-24 - Icon-only Button Accessibility
**Learning:** Providing explicit `aria-label` attributes for icon-only buttons ensures they are properly announced by screen readers, complementing visual `title` tooltips.
**Action:** Always include an `aria-label` when using icon-only buttons for actions like fullscreen, settings, and minimize.
