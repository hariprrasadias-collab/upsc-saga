## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2026-09-25 - Icon Button Accessibility
**Learning:** Icon-only buttons using raw text symbols (\342\234\225, \360\237\223\212, \342\232\231\357\270\217, \342\210\222, \342\234\223, \342\234\216) in utility components like timers are completely inaccessible to screen readers without ARIA labels, and raw symbols can be read aloud unhelpfully if not hidden with `aria-hidden="true"`.
**Action:** Always add `aria-label` to icon-only controls and wrap the visual symbol in `<span aria-hidden="true">`.
