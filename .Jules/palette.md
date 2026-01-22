## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-10-24 - Modal Focus Management
**Learning:** Modals that don't trap focus or manage it on mount leave keyboard users lost in the document body. Simple `useEffect` focus on the primary action and "Escape" key listeners make them feel native.
**Action:** Always add `role="dialog"`, `aria-modal="true"`, focus the main button on mount, and bind the Escape key for all overlay components.
