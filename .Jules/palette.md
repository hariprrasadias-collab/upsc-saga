## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-11-10 - Screen Reader Visibility of Close Buttons
**Learning:** Icon-only close buttons (like "✕" or "×") are completely unannounced by screen readers, leading to users getting trapped in modals or being unable to dismiss toast notifications and tooltips.
**Action:** Always provide an `aria-label="Close"` (or a similar contextual action descriptor like `"Cancel editing"`) for all buttons where the textual content consists entirely of symbols.
