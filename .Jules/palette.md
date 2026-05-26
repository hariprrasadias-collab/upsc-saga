## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2025-02-28 - Modal Close Button Accessibility
**Learning:** Close buttons using a visual '×' symbol are often announced as 'multiply' by screen readers.
**Action:** Wrap the '×' in `<span aria-hidden="true">×</span>` and apply a descriptive `aria-label` (e.g., 'Close dialog') to the parent `<button>` to ensure correct screen reader announcements.
