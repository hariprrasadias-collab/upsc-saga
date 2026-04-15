## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2026-04-14 - Added ARIA label to ModelAnswersManager close button
**Learning:** The 'x' close button inside modal dialogs in this repository lacks proper ARIA labels, potentially causing screen readers to misinterpret the button.
**Action:** Add explicit `aria-label` attributes to icon-only close buttons.
