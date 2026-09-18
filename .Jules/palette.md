## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2024-05-28 - Async Button State Feedback
**Learning:** For asynchronous actions (like claiming a daily challenge), users need immediate visual feedback while the request processes, otherwise they may click multiple times or assume the UI is broken. Combining `disabled`, `aria-busy`, and text changes provides both visual and screen-reader accessible loading states.
**Action:** Always implement a loading state for async submit buttons, ensuring to disable the button, set `aria-busy={true}`, and change the button text or display a spinner to indicate activity.
