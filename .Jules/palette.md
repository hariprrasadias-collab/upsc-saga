## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2026-04-13 - Icon-Only Action Buttons Need ARIA Labels
**Learning:** Icon-only action buttons (like Copy or Download) often lack textual labels, making them inaccessible to screen readers, even if they have  attributes.
**Action:** Always add explicit `aria-label` attributes to buttons that only contain icons to ensure their function is clearly conveyed to assistive technologies.
## 2024-05-23 - Icon-Only Action Buttons Need ARIA Labels
**Learning:** Icon-only action buttons (like Copy or Download) often lack textual labels, making them inaccessible to screen readers, even if they have `title` attributes.
**Action:** Always add explicit `aria-label` attributes to buttons that only contain icons to ensure their function is clearly conveyed to assistive technologies.
