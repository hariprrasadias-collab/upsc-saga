## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2024-04-26 - Add ARIA Labels to Pomodoro Timer
**Learning:** Found several icon-only buttons (Minimize, Close Fullscreen, Save Time, Cancel Edit) in `PomodoroTimer.tsx` that were missing `aria-label`s, making them opaque to screen readers. This is a common pattern to watch out for when adding utility buttons.
**Action:** Always ensure that icon-only interactive elements have an explicitly defined `aria-label` attribute if they lack discernible text or descriptive `title` attributes.
