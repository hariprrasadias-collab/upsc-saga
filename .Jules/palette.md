## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2024-05-24 - Icon-only Emoji Buttons Accessibility
**Learning:** Emoji icons inside buttons are read aloud by screen readers by their default descriptions, which may not provide context (e.g., 'crossed swords' instead of 'Mark Complete').
**Action:** When using emoji icons for buttons, wrap the emoji in `<span aria-hidden="true">`, and apply an `aria-label` to the parent button with clear context (e.g., 'Mark Activity as complete').
