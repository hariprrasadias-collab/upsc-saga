## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-05-23 - Icon-Only Controls Accessibility
**Learning:** Icon-only buttons relying purely on visual symbols (like emoji or SVGs) are inaccessible to screen reader users unless properly labeled. Also, assistive technologies may redundantly read both the visual character and semantic label if not handled.
**Action:** Always add descriptive `aria-label`s to icon-only buttons, and wrap the inner visual element (e.g., emojis or symbols) in `<span aria-hidden="true">` to prevent redundant reading.
