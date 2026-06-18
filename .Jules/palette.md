## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2024-06-18 - Improved Modal Accessibility
**Learning:** Custom modals like `ModelAnswersManager` need explicit ARIA attributes (`role="dialog"`, `aria-modal="true"`, `aria-labelledby`) and properly labeled close buttons (`<span aria-hidden="true">` for icons and `aria-label` on `<button>`) to ensure screen reader users can navigate them effectively.
**Action:** Always add ARIA attributes to custom modals and label icon-only close buttons correctly.
