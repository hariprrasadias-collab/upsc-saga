## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2025-02-15 - Pomodoro Timer Accessibility
**Learning:** Relying solely on the `title` attribute for icon-only buttons (like settings, fullscreen, and minimize controls) is insufficient for screen reader accessibility and violates a11y guidelines.
**Action:** Always include explicit `aria-label` attributes on `role="button"` elements that lack visible text content, ensuring screen readers announce the action properly.
