## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2026-09-17 - [Accessible Icon-Only Buttons]
**Learning:** When using raw text symbols or emojis in icon-only buttons within this app's Pomodoro components, screen readers attempt to read the literal characters unless specifically hidden. Combining `aria-label` on the button with `aria-hidden="true"` on a span wrapping the symbol is required for a clean accessibility experience.
**Action:** Always wrap literal icon symbols in `<span aria-hidden="true">` when providing an `aria-label` for an icon-only button.
