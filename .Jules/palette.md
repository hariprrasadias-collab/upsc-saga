## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2024-05-23 - Pomodoro Timer Accessibility
**Learning:** Icon-only buttons used for settings, mode switching, and controls in the Pomodoro Timer completely lacked context for screen readers. Using descriptive `aria-label`s on components like "Fullscreen" and "History" is critical for accessible interaction.
**Action:** Always ensure any button containing only an icon or emoji (like ⚙️, ✕, 📊) has a clear, descriptive `aria-label` explaining its function.
