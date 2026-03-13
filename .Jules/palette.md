## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-05-24 - Missing ARIA Labels on Icon-Only Buttons
**Learning:** Icon-only buttons using raw unicode characters (e.g. ⚔️, 🗠) or SVGs without proper `aria-label`s and `aria-hidden` spans render the component inaccessible to screen reader users, who will hear either nothing or an unintelligible pronunciation of the unicode symbol.
**Action:** When creating icon-only interactive elements, always provide an explicit descriptive `aria-label` on the button itself and wrap the raw unicode/emoji/SVG inside a `<span aria-hidden="true">` to hide it from assistive technologies.
