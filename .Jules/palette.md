## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2024-09-27 - Aria Labels for Icon Buttons
**Learning:** Icon-only buttons with emojis like `⚙️` or `📊` in PomodoroTimer component lack `aria-label` attributes and screen reader hiding for emojis, creating an inaccessible experience for screen readers.
**Action:** Add `aria-label` to these buttons and wrap emojis in `<span aria-hidden="true">`.
