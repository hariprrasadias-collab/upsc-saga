## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2026-04-06 - Add ARIA labels to icon-only controls
**Learning:** Relying on 'title' attributes for icon-only buttons (like settings, minimize, edit) is a common accessibility trap; it doesn't adequately announce the button's action to screen readers. For interactive widgets, explicit 'aria-label' and structural linkages like 'aria-expanded' / 'aria-controls' are required to properly communicate state.
**Action:** Always ensure icon-only buttons receive descriptive 'aria-label' properties. Additionally, when buttons control expandable areas like panels or modals, include 'aria-expanded' and 'aria-controls'.
