## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2025-03-12 - Custom Checkbox Screen-Reader Accessibility
**Learning:** When building custom checkboxes by hiding the native `<input type="checkbox">` visually and using CSS pseudo-elements or sibling elements, the native input's state is what is read by screen readers. If it doesn't have an explicit label natively associated with it via `id`/`htmlFor` or `aria-label`, the screen reader user will just hear "checkbox, unchecked" without knowing what action the checkbox performs.
**Action:** Always provide an explicit `aria-label` attribute on the hidden `<input type="checkbox">` that describes exactly what toggling it will do when an explicit associated `<label>` text sibling is missing.
