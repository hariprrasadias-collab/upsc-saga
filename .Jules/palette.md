## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2026-08-18 - ARIA labels for icon-only buttons
**Learning:** Icon-only close buttons (like "×") in modals and reports need explicit `aria-label`s so screen readers announce their function instead of just reading "times" or ignoring them.
**Action:** Always add descriptive `aria-label` (e.g., "Close report", "Close modal") to buttons that rely solely on visual icons.
