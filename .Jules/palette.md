## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2026-04-20 - Adding ARIA Labels to Pomodoro Timer Controls
**Learning:** Standard `title` attributes on icon-only timer control buttons are insufficient for screen readers; `aria-label` attributes must be explicitly declared for accessibility.
**Action:** Add `aria-label` alongside or instead of `title` on all icon-only interactive UI components, specially floating controls like timers.
