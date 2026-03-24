## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2026-03-23 - Screen Reader Support for Interactive Widgets & Icon-only Buttons
**Learning:** Custom interactive elements (e.g. `pomodoro-minimized`) and icon-only buttons using unhelpful unicode symbols require specific ARIA attributes to be usable by screen readers. For interactive divs, `role="button"`, `tabIndex={0}`, `aria-label`, and an `onKeyDown` handler capturing 'Enter' and 'Space' are essential. For buttons with emojis, wrapping the emoji in `<span aria-hidden="true">`, while setting the `aria-label` on the button itself, correctly announces the action while silencing the irrelevant unicode description.
**Action:** Ensure all non-button interactive widgets include full keyboard accessibility attributes, and all icon-only buttons rely on `aria-label` alongside `aria-hidden` for their visual contents.
