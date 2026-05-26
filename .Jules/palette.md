## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-05-26 - Close Button Accessibility
**Learning:** Custom visual close buttons (`×`) often lack semantic meaning, rendering them invisible or confusing to screen reader users. Adding an `aria-label` along with `aria-hidden="true"` on the visual icon element ensures that screen readers announce the button's function instead of attempting to read the symbol itself.
**Action:** Always add `aria-label="Close"` to close buttons and hide the visual symbol using `aria-hidden="true"` to provide a seamless and accessible experience.
