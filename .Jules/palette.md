## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-05-24 - ARIA Controls in Collapsible Menus
**Learning:** Collapsible components (like sidebars and accordions) require an `aria-controls` attribute on the trigger button to reference the exact `id` of the content container, complementing `aria-expanded` so screen readers properly associate the toggle with the content it reveals.
**Action:** Always link toggle buttons and their expandable content areas using `aria-controls` and `id` pairs to ensure full screen reader support.
