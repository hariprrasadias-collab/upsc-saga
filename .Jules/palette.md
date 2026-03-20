## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2026-03-20 - Icon-Only Interactive Elements Accessibility
**Learning:** When using raw unicode, emoji, or SVGs as the visual component of icon-only buttons or interactive elements, screen readers may attempt to literally pronounce the symbol, resulting in confusing announcements.
**Action:** Always provide an explicit descriptive `aria-label` on the button itself and wrap the raw unicode, emoji, or SVG inside a `<span aria-hidden="true">`. This ensures assistive technologies ignore the symbol and correctly announce the component's intent.
