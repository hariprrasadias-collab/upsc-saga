## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2025-02-12 - Icon-only buttons accessibility
**Learning:** Emoji/icon-only buttons using `title` attributes alone fail to provide sufficient context to screen readers, making core controls inaccessible.
**Action:** Always provide explicit `aria-label` attributes for icon-only interactive elements and use `aria-expanded` for toggle controls to ensure a fully accessible UX for assistive technologies.
