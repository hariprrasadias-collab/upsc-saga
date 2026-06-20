## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-06-20 - Evaluation Report Accessibility
**Learning:** Adding screen reader support for standalone dynamic pop-up modals requires more than just styling; they need explicit `role="dialog"`, `aria-modal="true"`, and an internal label (`aria-labelledby` linked to the modal title) so that users navigating via assistive tools immediately understand the newly rendered context. Close buttons displaying raw characters like "×" must be wrapped in `aria-hidden` with a textual label on the parent button.
**Action:** Always verify custom modal overlays have the explicit dialog ARIA footprint and visually-only symbols are concealed from screen readers.
