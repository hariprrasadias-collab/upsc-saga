## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-08-08 - Icon-Only Button Accessibility
**Learning:** Screen readers may redundantly read both the visual character (like an emoji) and the aria-label on icon-only buttons if the visual character isn't hidden.
**Action:** Always wrap inner visual elements (e.g., emojis or symbols) of icon-only buttons in `<span aria-hidden="true">` while providing a descriptive `aria-label` on the parent button.
