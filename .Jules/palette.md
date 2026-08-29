## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2024-08-29 - Missing ARIA Labels on Pomodoro Widget Icon-only Controls
**Learning:** Found a pattern in widget components like `PomodoroTimer` where numerous icon-only buttons (Fullscreen, History, Settings, Minimize) completely lacked accessible names, making the controls invisible to screen readers.
**Action:** Always verify that every action button, especially within dense UI widgets and interactive panels, has a clear `aria-label` or explicit text content when relying solely on icons.
