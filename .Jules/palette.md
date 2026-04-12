## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2026-04-12 - Adding ARIA labels to RevisionWidget buttons
**Learning:** Relying solely on `title` attributes is insufficient for screen reader accessibility in React applications.
**Action:** Add explicit `aria-label` attributes matching `title` text for icon-only buttons to guarantee announcement by screen readers, particularly those operating via emojis.
