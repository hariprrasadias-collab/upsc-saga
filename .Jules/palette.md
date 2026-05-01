## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2026-05-01 - Add ARIA label to close buttons
**Learning:** Icon-only close buttons using special characters (like '×') are completely opaque to screen readers without ARIA labels.
**Action:** Always verify that '×' buttons include descriptive aria-label attributes.
