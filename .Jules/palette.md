## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2025-04-08 - ARIA Labels for Timers
**Learning:** Relying solely on title attributes for icon-only buttons in timer elements is insufficient for screen reader accessibility.
**Action:** Ensure explicit aria-label attributes are applied to all icon-only buttons, specifically in dynamically updating interfaces like timers.
