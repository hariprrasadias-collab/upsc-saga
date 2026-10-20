## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-05-28 - Missing ARIA Labels on Close Buttons
**Learning:** Across the application's components, multiple modal dialogs and overlays feature icon-only "✕" or "×" close buttons (e.g., `close-btn`, `close-modal-btn`) without screen reader accessible text.
**Action:** When implementing modal windows or overlays, ensure all icon-only close buttons include an explicit `aria-label="Close"` attribute so they are perceivable to screen reader users.
