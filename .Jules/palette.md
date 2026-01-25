## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-05-24 - Semantic Buttons for Accordions
**Learning:** Using `div`s with `onClick` for accordion headers excludes keyboard users and screen readers.
**Action:** Replace interactive `div`s with `<button type="button">`, employing CSS resets to maintain the design while gaining native focus and activation behavior.
