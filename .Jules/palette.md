## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-05-19 - Accessible Close Buttons
**Learning:** Found multiple instances of `×` or `✕` characters used as icon-only close buttons in various modals and overlays (e.g., `<button className="close-btn">` ). These buttons lacked ARIA labels, making them completely inaccessible to screen reader users who would only hear "button" or "multiply".
**Action:** Always add `aria-label="Close"` to any icon-only close button.
