## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-05-18 - Improve icon-only close button in Sidebar and Modals
**Learning:** Found a mobile close button in the Sidebar and many modals that had `aria-label` or lacked them completely, and lacked proper spacing or a visually hidden span for robust screen reader support/icon presentation. Often raw `×` characters can be read aloud weirdly.
**Action:** Enhance icon-only buttons by wrapping visual elements in `<span aria-hidden="true">` to prevent assistive technologies from misreading, keeping the label in `aria-label` or visually hidden text.
