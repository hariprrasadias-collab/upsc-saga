## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-05-24 - Accessible Close Buttons with Emojis
**Learning:** Icon-only close buttons using emojis (like ✕ or ×) are not inherently accessible and will be read out generically (e.g., "times" or "multiplication sign"). Furthermore, the emoji or character must be wrapped in an `aria-hidden="true"` span so the screen reader ignores it, relying on the `aria-label` attribute on the parent button.
**Action:** When using emoji or character icons for buttons, wrap the character in `<span aria-hidden="true">` and provide a clear `aria-label` like "Close" on the parent button.
