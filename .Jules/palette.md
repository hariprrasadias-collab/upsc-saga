## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2025-01-20 - Non-Blocking Feedback
**Learning:** Using `window.alert()` halts the entire browser thread and feels jarring. Replacing it with Toast notifications provides a smoother experience but requires careful management of async states (like button disabling) to prevent user confusion during the transition.
**Action:** Always prefer Toasts over Alerts for success/failure messages, and ensure the trigger button shows a loading state while the action completes.

## 2025-01-20 - Progress Bar Semantics
**Learning:** Visual progress bars (divs) are invisible to screen readers. Adding `role="progressbar"` along with `aria-valuenow`, `aria-valuemin`, and `aria-valuemax` makes them accessible.
**Action:** Always audit progress indicators for ARIA attributes.
