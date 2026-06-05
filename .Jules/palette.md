## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-06-05 - Icon Button Accessibility
**Learning:** Textual representations of icons (like "×" or "✕" for close buttons) can be confusing for screen readers and may be read as "multiply".
**Action:** When using textual icons, wrap the text in `<span aria-hidden="true">` to hide it from screen readers, and add a descriptive `aria-label` (e.g., "Close dialog") to the parent button.
