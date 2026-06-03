## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-05-24 - Modal Close Button Accessibility
**Learning:** For custom modals and dialogs across the app, close buttons using a visual '×' symbol should wrap the '×' in `<span aria-hidden="true">×</span>` and apply a descriptive `aria-label` (e.g., 'Close dialog') to the parent `<button>` to prevent screen readers from announcing 'multiply'.
**Action:** Always wrap visual '×' symbols with `<span aria-hidden="true">` and ensure the parent button has a descriptive `aria-label` when creating close buttons.
