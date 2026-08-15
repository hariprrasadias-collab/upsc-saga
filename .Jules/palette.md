## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-05-24 - Accessible Icon-Only Buttons
**Learning:** Adding `aria-label` to an icon-only button is not enough. Screen readers will read the `aria-label` AND the icon character (e.g., emoji) redundantly.
**Action:** When adding `aria-label` to icon-only buttons, ALWAYS wrap the visual character (emoji/symbol) in a `<span aria-hidden="true">` to hide it from assistive technologies.
