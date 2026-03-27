## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2024-03-27 - [Sidebar Accordion Missing ARIA Controls]
**Learning:** When building custom accordion or collapsible group UIs, `aria-expanded` alone is insufficient. Screen readers require the toggle button to explicitly declare which region it commands via `aria-controls` mapped to the target content container `id`.
**Action:** Always pair `aria-expanded` with `aria-controls` when creating accessible collapsible sections.
