## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2025-04-09 - Accessible Emoji Icons
**Learning:** Icon-only interactive elements using emojis or symbols must have appropriate `aria-label`s. More critically, the literal emojis themselves should be wrapped in `<span aria-hidden="true">` to prevent screen readers from awkwardly reading out symbol/emoji names instead of or alongside the provided label.
**Action:** Always wrap standard interactive emojis and text symbols in `<span aria-hidden="true">` when adding `aria-label`s to parent buttons.
