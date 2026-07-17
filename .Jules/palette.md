## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2025-01-22 - Modal Accessibility & Close Buttons
**Learning:** Custom modals must use `role="dialog"` and `aria-modal="true"` to trap screen reader focus properly, while linking to a heading via `aria-labelledby`. Additionally, icon-only close buttons (like '×') can be misread by screen readers (e.g., as "multiplication sign") unless wrapped in an `aria-hidden` span with a clear `aria-label` on the parent button.
**Action:** Always apply dialog roles and aria-labelledby to modal containers, and ensure all icon-only close buttons are properly labeled and hidden from screen readers.
