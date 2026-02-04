## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-05-23 - Accordion Header Accessibility
**Learning:** Accordion headers implemented as `div`s with `onClick` are inaccessible to keyboard users and screen readers.
**Action:** Use `<button>` elements for headers with `aria-expanded` and `aria-controls`. Reset button styles in CSS to maintain the design while gaining native accessibility.
