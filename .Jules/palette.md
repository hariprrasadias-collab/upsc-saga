## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-05-24 - Icon-only Button Accessibility
**Learning:** When making UX improvements to icon-only buttons by adding `aria-label`, the inner visual element (e.g., emojis or symbols like `×`) must be wrapped in `<span aria-hidden="true">`. Without this, screen readers will redundantly read the visual character alongside the semantic label (e.g., 'Close report times').
**Action:** Always wrap visual elements in `aria-hidden="true"` when applying an `aria-label` to their parent button.
