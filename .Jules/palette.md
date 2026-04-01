## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-05-24 - Collapsible Menu Accessibility
**Learning:** When creating collapsible or expandable UI components (like sidebars or accordions), the toggle button needs `aria-controls` referencing the exact `id` of the collapsible content container to comply with accessibility standards.
**Action:** Always include `aria-controls` on group toggle buttons in combination with `aria-expanded`.
