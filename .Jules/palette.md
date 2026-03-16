## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2026-03-16 - Icon-Only Button Accessibility in Pomodoro Timer
**Learning:** Discovered icon-only buttons in the Pomodoro Timer lacked explicit `aria-label` attributes and properly hidden icon characters using `<span aria-hidden="true">`. While `title` provides tooltip hints for sighted users, assistive technologies need semantic text descriptions via `aria-label` to announce actions correctly instead of attempting to pronounce raw unicode/emoji characters.
**Action:** Update all icon-only buttons to include descriptive `aria-label` attributes and wrap raw unicode/emoji icons in `<span aria-hidden="true">`. Ensure this pattern is consistently applied across the codebase for custom interactive elements.
