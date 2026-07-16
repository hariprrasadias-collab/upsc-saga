## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2024-05-23 - Pomodoro Timer Accessibility
**Learning:** Icon-only buttons without proper ARIA labels are a common accessibility issue for components like custom timers. Even when a `title` attribute is present, adding an explicit `aria-label` provides reliable screen reader support.
**Action:** When creating or maintaining timer controls and generic UI action buttons (like edit, save, minimize), always ensure explicit `aria-label` attributes are present.
