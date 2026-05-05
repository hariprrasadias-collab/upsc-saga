## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-05-23 - Modal Close Button Accessibility
**Learning:** Close buttons represented only by a visual "×" or "✕" character are announced confusingly by screen readers (e.g., "multiply"). Wrapping the character in `<span aria-hidden="true">` and adding a descriptive `aria-label` to the button ensures correct announcement.
**Action:** Always provide an `aria-label` for icon-only close buttons, and hide the generic text icon from screen readers to prevent redundant or confusing readout.
