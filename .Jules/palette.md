## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-08-09 - Icon-Only Button Accessibility
**Learning:** When making UX improvements to icon-only buttons by adding `aria-label`, screen readers often redundantly read the visual character (like an emoji or symbol) alongside the semantic label if it is not explicitly hidden.
**Action:** Always wrap the inner visual element (e.g., emojis or symbols) in `<span aria-hidden="true">` when adding an `aria-label` to the parent button, to prevent assistive technologies from redundantly reading the visual character.
