## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2026-01-25 - Accessible Typing Effects
**Learning:** Animated typing text effects are visually engaging but problematic for screen readers, which may announce partial words or nothing until the animation completes.
**Action:** When implementing typing effects, always provide the full text in a `sr-only` (visually hidden) element and hide the animated element from screen readers using `aria-hidden="true"`.
