## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-06-19 - Accessible Icon Buttons
**Learning:** Screen readers announce symbols visually when read aloud (e.g., 'multiply' for '×', 'downwards arrow' for '↙️') which is confusing for icon-only buttons.
**Action:** Always wrap emoji or visual text cues inside a `<span aria-hidden="true">` on icon-only buttons and add a descriptive `aria-label` to the parent `<button>`.
