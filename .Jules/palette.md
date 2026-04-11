## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2026-04-11 - Added ARIA labels to PomodoroTimer Controls
**Learning:** Relying solely on 'title' attributes is insufficient for screen reader users, especially for icon-only control interfaces like timers. We must always provide explicit 'aria-label' attributes.
**Action:** When creating or modifying widgets with symbol/icon-based buttons, ensure 'aria-label' is included alongside 'title'.
