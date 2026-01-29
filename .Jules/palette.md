## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-05-24 - Interactive Elements Semantics
**Learning:** Clickable `div`s with `onClick` handlers are invisible to keyboard users and lack semantic meaning. Replacing them with `<button>` elements provides native keyboard support (Focus, Enter/Space) but requires explicit CSS resets (font inheritance, border removal) to preserve visual design.
**Action:** Default to `<button type="button">` for any interactive element that isn't a link, using a "reset" CSS class to strip default styles if a custom look is required.
