## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-05-24 - Async Button Feedback
**Learning:** Simply disabling a button during async operations is insufficient if the component state resets immediately (e.g., stopping a timer resets to 'Start'). Users miss the 'Saving...' feedback entirely.
**Action:** Implement a dedicated `isSubmitting` state that explicitly overrides the default UI controls (hiding 'Start'/'Stop') to persist the loading feedback until the async operation completes.
