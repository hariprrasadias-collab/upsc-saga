## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-05-31 - Close Button Accessibility
**Learning:** Screen readers often read the `&times;` symbol as "multiply". For icon-only close buttons, wrapping the visual symbol in an `aria-hidden="true"` element prevents confusing announcements, while an explicit `aria-label` on the parent `<button>` provides the correct context.
**Action:** Always wrap visual text icons like '×' in `<span aria-hidden="true">` and provide a descriptive `aria-label` (e.g., 'Close dialog') on the interactive element.
