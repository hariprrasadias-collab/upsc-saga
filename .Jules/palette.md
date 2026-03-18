## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-05-23 - Icon-only Buttons Accessibility
**Learning:** Icon-only close buttons (like "×" or "✕") are widespread in application modals but are often unhelpful or confusing for screen reader users when missing `aria-label`. Moreover, the raw text node for the icon itself can be announced unexpectedly.
**Action:** Always provide an explicit, descriptive `aria-label` (e.g., "Close modal", "Exit fullscreen") on icon-only buttons, and wrap the raw unicode character or SVG inside a `<span aria-hidden="true">` to ensure assistive technologies read the intended label instead of attempting to pronounce the symbol.
