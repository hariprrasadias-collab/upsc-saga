## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2024-11-20 - Aria-labels in Boss Arena
**Learning:** Icon-only or ambiguous buttons (like '✕ End Battle' and 'Cancel') in the Boss Arena components lack context for screen readers.
**Action:** Added aria-label attributes to these buttons to provide clear context for visually impaired users without altering visual design.
