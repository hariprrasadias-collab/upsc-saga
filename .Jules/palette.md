## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2024-07-18 - Missing Aria-labels on modal and chat components
**Learning:** Icon-only close buttons (✕, ×) and icon-only send buttons (➤) heavily lack `aria-label` attributes across different modal, sidebar, and chat interfaces. Many modals only include a visible `✕` character, leading screen readers to read "times" or "multiplication X", which makes the navigation inaccessible.
**Action:** Always wrap these icon-only characters in `<span aria-hidden="true">` and apply the `aria-label="Close"` or `aria-label="Send message"` directly on the parent `<button>`.
