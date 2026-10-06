## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2024-10-06 - Missing ARIA Labels on Close Buttons
**Learning:** Many modal components across the app use standard HTML buttons with text content like "×" or "✕" for closing, but lack semantic `aria-label` attributes. This makes screen readers read out literal characters like "multiply" rather than providing actionable context to visually impaired users.
**Action:** Enforce a standard where any icon-only button or single-character button (especially modals and alerts) strictly requires an `aria-label="Close"`.
