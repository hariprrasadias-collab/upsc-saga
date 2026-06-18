## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2026-06-17 - Modal Close Button Accessibility
**Learning:** Icon-only close buttons in modals (like ) are often inaccessible to screen readers because they lack descriptive text.
**Action:** Always add an  or similar descriptive label to icon-only buttons to ensure they are fully accessible.
## 2024-05-23 - Modal Close Button Accessibility
**Learning:** Icon-only close buttons in modals (like `×`) are often inaccessible to screen readers because they lack descriptive text.
**Action:** Always add an `aria-label="Close modal"` or similar descriptive label to icon-only buttons to ensure they are fully accessible.
