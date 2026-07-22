## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2024-05-23 - Icon-Only Button Accessibility in Admin Dashboard
**Learning:** Icon-only buttons (like edit `✏️` and delete `🗑️`) are entirely invisible to screen readers without descriptive labels, leaving users guessing their function.
**Action:** Always add clear, descriptive `aria-label` attributes to any interactive element that relies solely on icons or visual cues for its meaning.
