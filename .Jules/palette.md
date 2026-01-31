## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-05-28 - Toast Interaction Timing
**Learning:** Auto-dismissing toasts can frustrate users if they disappear while being read or interacted with. Pausing the timer on hover/focus is a critical accessibility pattern (WCAG 2.1 SC 2.2.1) often missed in custom implementations.
**Action:** Implement `onMouseEnter`/`onFocus` handlers to pause dismissal timers and CSS animations on all transient UI elements.
