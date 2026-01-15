## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-05-23 - Custom Progress Bars
**Learning:** Custom div-based progress bars in dashboard widgets lack semantic ARIA roles, making them invisible to screen readers.
**Action:** Always add role="progressbar" and aria-value* attributes to visual progress indicators.
