## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2024-05-23 - Collapsible Group Accessibility
**Learning:** For accessibility in collapsible or expandable UI components (like sidebars or accordions), the toggle button (`aria-expanded`) must always be complemented by an `aria-controls` attribute referencing the exact `id` of the collapsible content container, allowing screen readers to logically link the trigger and the content.
**Action:** Always ensure any button that expands/collapses content has a matching `aria-controls` attribute pointing to the ID of the container it controls.
