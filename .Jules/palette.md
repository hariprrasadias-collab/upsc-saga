## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2024-08-27 - Icon-only Buttons Accessibility
**Learning:** Icon-only buttons (like close buttons using `\303\227` or `\342\234\225`) are inaccessible to screen readers without a proper descriptive label, leading to poor navigation experiences for assistive technologies.
**Action:** Always provide an `aria-label` (e.g., `aria-label="Close"`) to buttons that lack descriptive text content to ensure accessibility.
