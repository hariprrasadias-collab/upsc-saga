## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-10-24 - Expandable Section Accessibility
**Learning:** Collapsible sections (like accordions) require `aria-controls` on the trigger button pointing to the content container's ID to programmatically link them for screen readers.
**Action:** Ensure every toggle button has `aria-controls="[ID]"` and the content container has the matching `id`.
