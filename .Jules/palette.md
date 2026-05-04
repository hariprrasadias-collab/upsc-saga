## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2026-05-04 - Adding ARIA labels to icon-only buttons
**Learning:** React elements like `<button>×</button>` without descriptive text are inaccessible to screen readers.
**Action:** Always verify icon-only buttons have an appropriate `aria-label` (e.g., `aria-label="Close report"`) to ensure screen reader accessibility without adding visual clutter.
