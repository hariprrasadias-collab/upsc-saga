## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2024-05-23 - Custom Modals Close Buttons
**Learning:** Custom modals across the app often use a raw '×' character for close buttons. This causes screen readers to announce 'multiply'.
**Action:** Always wrap visual '×' characters in `<span aria-hidden="true">×</span>` and apply a descriptive `aria-label` (e.g., 'Close [component]') to the parent `<button>`.
