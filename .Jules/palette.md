## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2026-02-05 - Custom Checkbox Accessibility
**Learning:** Custom checkboxes implemented with sibling elements (e.g., `input + span`) often hide the visual label in a separate container. This disconnects the label from the input for screen readers.
**Action:** Always add an explicit `aria-label` to the hidden input when the visual label is not associated via `label` element nesting or `for/id` attributes.
