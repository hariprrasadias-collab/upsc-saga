## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2024-06-22 - Modal Dialog Accessibility
**Learning:** Shared modals require `aria-modal="true"`, `role="dialog"`, and explicit IDs linked to the title via `aria-labelledby`. Close buttons with visual elements like '×' need their icons wrapped in `aria-hidden="true"` and an `aria-label` on the button itself.
**Action:** Consistently enforce accessibility on all reusable modal dialogs to support screen readers and keyboard navigation.
