## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-05-24 - Icon-only Button Accessibility
**Learning:** Icon-only buttons (like modal close buttons containing just an '×' character) without `aria-label`s are completely opaque to screen readers. Furthermore, the inner visual character itself should be explicitly hidden (`aria-hidden="true"`) to prevent assistive technologies from reading redundant or confusing content (like "times" or "multiplication sign") alongside the semantic label.
**Action:** Always provide descriptive `aria-label` attributes on icon-only buttons and wrap their inner text/symbols with `<span aria-hidden="true">`.
