## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2024-06-14 - Improve Pomodoro Timer Accessibility
**Learning:** Found several icon-only buttons in the Pomodoro Timer component lacking `aria-label`s, which is critical for screen reader users to understand the button's function.
**Action:** Always verify icon-only buttons have descriptive `aria-label`s during code reviews and component development.
