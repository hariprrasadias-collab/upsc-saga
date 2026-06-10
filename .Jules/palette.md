## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2025-02-27 - Close Button Accessibility
**Learning:** Screen readers often announce the '×' or '&times;' symbol as 'multiply', which is confusing when used as a close button.
**Action:** Always wrap visual '×' symbols in `<span aria-hidden="true">&times;</span>` and ensure the parent `<button>` has a clear `aria-label` like "Close dialog" across all custom modals.
