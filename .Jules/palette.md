## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2026-09-11 - Expandable Group Accessibility
**Learning:** Screen readers need to know which content block an expandable button controls to properly convey the structure to users.
**Action:** Always link expandable headers to their content using `aria-controls="id"` and `id="id"`.
