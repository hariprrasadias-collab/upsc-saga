## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2024-06-19 - Accessible Pomodoro Controls
**Learning:** Icon-only buttons with `title` attributes are not fully accessible; they need explicit `aria-label` attributes for screen readers to properly announce their function.
**Action:** Always ensure icon-only control buttons, especially in compact interfaces like timers, have clear `aria-label`s.
