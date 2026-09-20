## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2024-05-20 - Accessible Icon Buttons
**Learning:** Icon-only buttons using raw text/emojis require `aria-hidden="true"` on an inner `span` alongside the `aria-label` on the `button`, otherwise screen readers may redundantly read the raw character along with the intended label.
**Action:** Always wrap raw text icons/emojis in `<span aria-hidden="true">` when applying `aria-label`s to buttons in the design system.
