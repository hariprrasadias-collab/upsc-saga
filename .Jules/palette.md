## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2024-05-24 - Accessibility on Icon-only buttons
**Learning:** Icon-only buttons in tools like the Pomodoro timer should have `aria-label`s to improve accessibility for screen readers. Inputs in forms that don't have visual labels should also include `aria-label` attributes to clarify their purpose.
**Action:** Always add `aria-label` to buttons relying exclusively on icons or symbols (e.g. ✕, ⛶, 📊, ⚙️, −, ✓, ✎) to describe their function, and to inputs that lack visual labels (like a standalone edit minute input).
