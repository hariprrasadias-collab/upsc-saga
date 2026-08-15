## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2024-05-23 - Pomodoro Timer Accessibility
**Learning:** Icon-only buttons used for timer controls and settings in the Pomodoro Timer component lack proper aria-labels, making them completely inaccessible to screen reader users who cannot interpret the visual meaning of the emojis or SVGs.
**Action:** Ensure all interactive elements that do not contain visible text (like toggle, close, and edit buttons) are provided with descriptive `aria-label` attributes to convey their purpose to assistive technologies.
