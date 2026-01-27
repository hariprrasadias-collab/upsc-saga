## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-06-18 - Overlay Panel Accessibility
**Learning:** Custom overlay/settings panels often lack basic accessibility features like `role="dialog"` and explicit Close buttons, relying only on toggle buttons outside the panel. This traps keyboard users or leaves them unsure how to exit.
**Action:** Always wrap custom overlays in `role="dialog"`, provide a labeled Close button inside the panel, and ensure proper ARIA labelling for all interactive elements.
