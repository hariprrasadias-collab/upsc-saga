## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-07-18 - Modal & Icon-Only Button Accessibility
**Learning:** Custom modals are invisible to screen readers without standard ARIA attributes (`role="dialog"`, `aria-modal="true"`), and icon-only close buttons (like '×') are read as confusing characters if not properly hidden.
**Action:** Ensure all custom modals use proper dialog roles and labels (`aria-labelledby`). Wrap visual close icons in `<span aria-hidden="true">` and provide a clear `aria-label` on the parent button.
