## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2026-08-17 - Icon-Only Button Accessibility
**Learning:** Icon-only buttons (like '\303\227' for close) are often unreadable to screen readers without descriptive labels.
**Action:** Always add an `aria-label` (e.g., `aria-label="Close"`) to buttons that only contain icons or symbols to ensure screen reader compatibility.
