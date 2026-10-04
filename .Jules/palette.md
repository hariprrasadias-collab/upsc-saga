## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2026-10-04 - Accessible Emoji Buttons
**Learning:** Icon-only buttons containing emojis or Unicode characters are read verbatim by screen readers, which is unhelpful. Using `aria-label` alongside `<span aria-hidden="true">✎</span>` ensures users understand the button's purpose without hearing literal character descriptions.
**Action:** Always wrap emoji or symbol icons in `aria-hidden="true"` spans and provide a descriptive `aria-label` on the parent button.
