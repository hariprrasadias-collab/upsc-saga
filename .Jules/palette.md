## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2024-05-15 - ARIA Labels on Pomodoro Timer Controls
**Learning:** The `PomodoroTimer` controls previously used emojis/symbols directly as text inside `<button>` elements (e.g., `⛶`, `✕`, `📊`, `⚙️`, `−`) without proper screen reader support.
**Action:** When adding accessible labels (`aria-label`) to icon-only buttons, always wrap the visual icon itself in a `<span aria-hidden="true">` to prevent screen readers from reading raw unicode symbols alongside the intended label.
