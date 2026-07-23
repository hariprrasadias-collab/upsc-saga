## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2024-05-19 - ARIA Labels for Pomodoro Timer
**Learning:** Found multiple icon-only buttons (emoji or Unicode characters) in the Pomodoro Timer component lacking accessible names. Screen readers would announce the character directly, which may be confusing.
**Action:** Wrapped decorative emojis in `<span aria-hidden="true">` and applied descriptive `aria-label`s to the parent `<button>` elements to improve clarity for assistive technologies.
