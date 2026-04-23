## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2024-05-24 - Missing ARIA Labels on Close Buttons
**Learning:** Close buttons that only contain special characters like "×" are opaque to screen readers without an explicit `aria-label`.
**Action:** Always add descriptive `aria-label`s (e.g., `aria-label="Close report"`) to icon-only buttons like modals or alerts to ensure proper screen reader accessibility.
