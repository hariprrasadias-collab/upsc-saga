## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-05-24 - Screen Reader Interpretation of Close Buttons
**Learning:** Custom modals across the app frequently use the '×' or '&times;' symbol for close buttons without hiding it from screen readers, causing them to incorrectly announce "multiply" instead of "close".
**Action:** Always wrap the visual '×' in `<span aria-hidden="true">×</span>` and apply a descriptive `aria-label` (e.g., 'Close dialog') to the parent `<button>`.
