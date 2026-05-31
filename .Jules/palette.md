## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2025-02-23 - Accessibility of Modal Close Buttons
**Learning:** Icon-only close buttons (like those with "×") often confuse screen readers by being read literally (e.g., "times") when an `aria-label` is missing.
**Action:** Always wrap visual elements representing text-like actions in an `<span aria-hidden="true">` and provide a clear `aria-label` on the parent button element itself.
