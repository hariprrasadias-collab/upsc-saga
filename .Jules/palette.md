## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2024-07-07 - Close Button Accessibility
**Learning:** Found a recurring pattern in the frontend where modals use icon-only close buttons (like "✕") without labels.
**Action:** Always wrap visual symbols in `<span aria-hidden="true">` and add a descriptive `aria-label` to the parent `<button>` to ensure screen readers don't read out confusing character names.
