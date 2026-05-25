## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2026-05-24 - ARIA labels for Icon-only buttons
**Learning:** Icon-only buttons relying solely on `title` attributes or emoji content are often inaccessible to screen readers, leaving users guessing their function.
**Action:** Always add explicit `aria-label` attributes to icon-only buttons to guarantee a clear, accessible description for assistive technologies.
