## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-05-23 - Icon-Only Buttons Accessibility
**Learning:** Icon-only buttons (like those containing only the '×' character for closing modals) are completely opaque to screen readers.
**Action:** Always add descriptive `aria-label` attributes to icon-only buttons to ensure their purpose is communicated clearly to users relying on assistive technology.
