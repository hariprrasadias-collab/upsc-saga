## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-06-07 - Modal Accessibility
**Learning:** For custom modal dialog components to be properly announced by screen readers, their container elements must include `role="dialog"`, `aria-modal="true"`, and an `aria-labelledby` attribute that references the ID of the modal's heading element. Visible text cues in close buttons (like `&times;`) should be wrapped in an `aria-hidden="true"` span to prevent confusing screen reader announcements.
**Action:** Always include these ARIA attributes on custom modal implementations.
