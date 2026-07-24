## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2026-07-24 - Pomodoro Timer Accessibility
**Learning:** The `PomodoroTimer` component in this application had several icon-only buttons (like settings, minimize, history, and edit controls) that lacked screen-reader descriptions.
**Action:** Always ensure that any icon-only button used in custom interactive components is provided with an `aria-label` attribute describing its function.
