## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2024-06-25 - Pomodoro Timer Accessibility
**Learning:** Icon-only buttons in floating elements or complex timer components frequently lack `aria-label` attributes. Relying on `title` is insufficient for proper screen reader accessibility.
**Action:** When working on timer or complex UI widgets, explicitly verify that all icon-only control buttons (like settings, close, minimize, save, edit) have `aria-label` attributes.
