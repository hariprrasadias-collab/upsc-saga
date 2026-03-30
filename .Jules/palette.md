## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2026-03-30 - Expandable Group Accessibility
**Learning:** Expandable UI elements (like sidebar groups) using `aria-expanded` need a corresponding `aria-controls` attribute pointing to the ID of the expanding container to fully support screen reader functionality.
**Action:** When implementing any expandable/collapsible interaction, always pair `aria-expanded` with an `aria-controls` referencing the toggled container's explicit ID.
