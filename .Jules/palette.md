## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2024-09-04 - Adding aria-label to close buttons
**Learning:** Found multiple instances across the app where icon-only modal "close" buttons (using the '×' or '✕' symbol) lacked an `aria-label`. This makes these buttons completely inaccessible to screen readers, which often skip or mispronounce these geometric symbols.
**Action:** When implementing modales or closable cards with an "X" icon, always enforce adding `aria-label="Close"` to the button element. This ensures that the element is clearly described to assistive technologies.
