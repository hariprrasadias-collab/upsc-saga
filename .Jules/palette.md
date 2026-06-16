## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-05-23 - Interactive Elements Accessibility
**Learning:** Interactive widgets often use `div` elements with `onClick` handlers without proper keyboard support (`tabIndex`, `onKeyDown`) or semantic roles, making them inaccessible to keyboard and screen reader users. Icon-only buttons frequently lack `aria-label`s and `aria-hidden="true"` on the icons.
**Action:** Always ensure interactive `div` elements have `role="button"`, `tabIndex={0}`, and keyboard event handlers. Ensure icon-only buttons have descriptive `aria-label`s and their icons are hidden from screen readers.
