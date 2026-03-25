## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2026-03-24 - Pomodoro Timer Minimized State Accessibility
**Learning:** Interactive div elements acting as buttons require a suite of attributes to be accessible: `role="button"`, `tabIndex={0}`, `aria-label`, and an `onKeyDown` handler for the Space and Enter keys.
**Action:** Always ensure that any custom interactive elements have full keyboard and screen reader support.
