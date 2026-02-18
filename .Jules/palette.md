## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-06-25 - Toast Timer Control
**Learning:** Fixed duration for notifications can be frustrating for users who need more time to read. Implementing a pause-on-hover mechanism provides user control without adding UI complexity, satisfying WCAG 2.2.1 Timing Adjustable.
**Action:** Ensure all auto-dismissing notifications pause their timer when hovered or focused.
