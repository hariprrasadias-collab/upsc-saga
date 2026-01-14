## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-05-24 - Async Button Feedback
**Learning:** Users often click "Submit" buttons multiple times if there's no immediate visual feedback, leading to duplicate requests or frustration.
**Action:** Always implement a `disabled` state with a visible "Loading..." or "Saving..." text change on action buttons, combined with `aria-busy="true"` on the relevant container to inform assistive technology of the pending state.
