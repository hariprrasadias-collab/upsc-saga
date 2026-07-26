## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2026-07-26 - Accessibility of Textareas and Icon-Only Buttons
**Learning:** In React apps, <h3> visual headers above <textarea> elements do not automatically associate with the inputs for screen readers. Using aria-labelledby links the visual heading directly to the input. Additionally, close buttons represented purely by "×" characters without text or aria-labels are inaccessible to assistive technology.
**Action:** Explicitly add id attributes to visual headers and link them using aria-labelledby in form fields. Ensure all icon-only buttons (like "×" close buttons) contain an aria-label.
