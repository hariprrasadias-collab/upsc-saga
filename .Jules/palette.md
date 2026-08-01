## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2026-08-01 - Icon-only Buttons Accessibility
**Learning:** Icon-only buttons (like '×' for close or '📋' for copy) without `aria-label`s or `title`s are read ambiguously by screen readers (e.g., "times" or "clipboard"), causing confusion for users relying on assistive technology.
**Action:** Always apply descriptive `aria-label` attributes to icon-only buttons to convey their actual function (e.g. "Close dashboard") instead of relying purely on visual metaphors.
