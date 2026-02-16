## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2025-05-27 - Custom Checkbox Accessibility
**Learning:** Custom checkboxes using hidden inputs often fail accessibility checks because the focus indicator is lost on the hidden element, and label association is broken if the text is outside the wrapping label.
**Action:** Use `:focus-visible` on the hidden input to style the visible custom replacement, and ensure `aria-label` or `aria-labelledby` is present on the input to describe its purpose.
