## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2026-04-10 - Add ARIA Labels to Pomodoro Timer Controls
**Learning:** Icon-only buttons used for essential controls like minimizing, toggling history/settings, or full screen within a floating widget must have explicit `aria-label` attributes to be properly announced by screen readers, because the `title` attribute alone is insufficient for robust accessibility.
**Action:** When adding new icon-based controls, always define an `aria-label` alongside `title` to communicate the control's purpose clearly to assistive technologies.
