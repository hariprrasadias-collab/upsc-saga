## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-05-23 - Icon-Only Button Accessibility Pattern
**Learning:** The symbol `×` (and `✕`) are commonly used for close buttons in modals, but without an `aria-label`, screen readers often read them literally (e.g., "times", "multiply") or ignore them entirely, leaving users confused about the button's purpose.
**Action:** When implementing icon-only buttons using typography or SVGs, always add an explicit `aria-label` (e.g., `aria-label="Close"`) and wrap the decorative character in a `<span aria-hidden="true">` to prevent the screen reader from reading the unhelpful visual symbol.
