## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2026-04-07 - Icon-only Button Accessibility
**Learning:** Relying solely on `title` attributes for icon-only buttons is insufficient for screen readers and can leave users unaware of the button's purpose.
**Action:** Always provide an explicit `aria-label` alongside or instead of `title` for any icon-only button (e.g. settings, close, minimize) to ensure full accessibility.
