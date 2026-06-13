## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2024-05-14 - Missing ARIA Labels on Icon-only Modals
**Learning:** Icon-only close buttons (like `×` in modal dialogs such as the Scribe Evaluation Report) lack programmatic labels throughout the application, making them inaccessible to screen readers.
**Action:** Always verify that icon-only buttons (`×`, `⚙️`, etc.) include explicit `aria-label` or `title` attributes (e.g., `aria-label="Close"`) when building or modifying components to ensure proper keyboard and screen reader accessibility.
