## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2026-07-29 - Close Button Accessibility
**Learning:** Icon-only close buttons (like × or ✕) are common in modals but are read ambiguously (e.g., "times" or "multiplication X") by screen readers if unlabeled, causing confusion.
**Action:** Always add explicit `aria-label="Close"` to icon-only close buttons across the application's modals, tooltips, and overlay components.
