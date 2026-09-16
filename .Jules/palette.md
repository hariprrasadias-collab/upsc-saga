## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-05-20 - [PomodoroTimer Icon-Only Buttons Accessibility]
**Learning:** Found several icon-only buttons in the PomodoroTimer component (fullscreen, history, settings, etc.) that used raw emojis/symbols without `aria-label`s, causing screen readers to read literal characters.
**Action:** Added descriptive `aria-label`s to these buttons and wrapped the symbols in `<span aria-hidden="true">` to prevent unhelpful readouts.
