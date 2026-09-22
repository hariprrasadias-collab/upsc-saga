## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2024-05-24 - Icon Button Accessibility
**Learning:** Icon-only buttons with text symbols are read literally by screen readers unless wrapped in <span aria-hidden="true"> and accompanied by an aria-label on the button.
**Action:** Always hide literal symbols from screen readers and provide descriptive aria-labels for icon buttons.
