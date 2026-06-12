## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2024-06-18 - Modal Close Button Accessibility
**Learning:** Screen readers announce visual symbols like `&times;` or `×` as "multiply" or "times", which causes confusion. Applying `aria-label="Close dialog"` to the parent button and wrapping the character in `<span aria-hidden="true">` prevents this issue.
**Action:** Always wrap visual '×' icons in `<span aria-hidden="true">` and use descriptive aria-labels on the parent button.
