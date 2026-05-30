## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2024-05-24 - Accessibility of "×" close buttons
**Learning:** Screen readers announce the "×" character as "multiply" in close buttons which is confusing.
**Action:** When using visual "×" characters as close icons, wrap them in `<span aria-hidden="true">×</span>` and add an `aria-label` like "Close" to the parent `<button>`.
