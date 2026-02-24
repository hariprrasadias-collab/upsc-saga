## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-05-28 - Progress Bar Accessibility
**Learning:** Visual progress bars (like XP meters) implemented with `div`s are completely invisible to screen readers without explicit ARIA roles.
**Action:** Always use `role="progressbar"` and provide `aria-valuenow`, `aria-valuemin`, `aria-valuemax`, and a descriptive `aria-label` for any custom progress component.
