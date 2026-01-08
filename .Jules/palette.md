## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-05-23 - Command Palette Discoverability
**Learning:** Power user features (like Command Palette) hidden behind keyboard shortcuts (Ctrl+K) are often undiscoverable and inaccessible to mouse/touch users.
**Action:** Always provide a visible trigger (e.g., a search icon button) for global shortcuts, complete with tooltips teaching the shortcut.
