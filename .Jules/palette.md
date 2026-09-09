## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-09-09 - Accordion Keyboard Accessibility
**Learning:** Custom interactive div elements acting as accordions (like sector and subject headers in SyllabusTracker) are invisible to keyboard users without explicit attributes. They require `role="button"`, `tabIndex={0}`, `aria-expanded`, and key handlers for Enter/Space to ensure full keyboard navigation and screen reader support.
**Action:** Always add keyboard accessibility attributes and handlers when converting static `div` elements into interactive, clickable UI components.
