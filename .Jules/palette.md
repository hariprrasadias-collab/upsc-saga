## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-06-25 - Icon-only Buttons Accessibility
**Learning:** Icon-only buttons relying purely on `title` attributes are often poorly supported by screen readers and touch devices.
**Action:** Ensure all icon-only interactive elements always have an explicit `aria-label` describing the action, in addition to visual tooltips.
