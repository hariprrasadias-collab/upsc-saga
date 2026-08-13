## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2026-08-12 - Accessible Icon-Only Buttons in Pomodoro Timer
**Learning:** Interactive timer interfaces often use compact, icon-only buttons (like settings, edit, and fullscreen toggles) that rely solely on `title` attributes or visual emojis, which can be missed or misinterpreted by assistive technologies.
**Action:** Consistently apply `aria-label` attributes to all icon-only buttons to guarantee that their purpose is explicitly announced to screen reader users, independently of tooltips or visual styling.
