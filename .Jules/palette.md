## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-05-24 - Icon-only Buttons Accessibility
**Learning:** Icon-only buttons without aria-labels are completely inaccessible to screen readers, and screen readers will often read out the Unicode emoji representation or raw text like 'x' or 'minus' which can be confusing out of context.
**Action:** Always add descriptive `aria-label` attributes to icon-only buttons, and wrap the icon content in `<span aria-hidden="true">`, particularly important for emoji or symbolic text buttons to prevent screen readers from reading out unhelpful literal characters.
