## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-05-23 - Modal Dialog Accessibility
**Learning:** Custom modal dialogs (like those in Scribe components) must explicitly include `role="dialog"`, `aria-modal="true"`, and `aria-labelledby` referencing the title's ID so screen readers can correctly identify and announce them as modal overlays, distinguishing them from inline content. Close buttons represented by symbols like `&times;` (`×`) should be wrapped in an `aria-hidden="true"` span and given a descriptive `aria-label` to ensure they are announced properly.
**Action:** Always add proper ARIA dialog attributes to the container and ensure close buttons have screen-reader-friendly text.
