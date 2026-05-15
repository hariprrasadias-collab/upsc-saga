## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2024-05-23 - Modal Dialog Accessibility
**Learning:** For overlay elements to be properly announced by screen readers as modal dialogs, they require a specific combination of attributes on the modal container (`role="dialog"`, `aria-modal="true"`, and `aria-labelledby` referencing a heading element) alongside descriptive `aria-label`s and visually hidden (`aria-hidden="true"`) cues for icon-only close buttons.
**Action:** When implementing custom modal components, always apply the `dialog` role pattern to the content wrapper, establish a relationship with the modal's title using `aria-labelledby`, and ensure interactive icon buttons announce their function rather than their symbol.
