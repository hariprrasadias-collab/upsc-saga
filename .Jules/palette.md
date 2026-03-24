## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2025-03-03 - Added aria-controls to Sidebar Expandable Groups
**Learning:** For collapsible content (like the Sidebar navigation groups), providing an \`aria-controls\` attribute on the toggle button that references the exact \`id\` of the content container is necessary to correctly link the button to the expandable content, which compliments the \`aria-expanded\` state for screen reader accessibility.
**Action:** When creating custom collapsible components or accordions in this application, ensure the toggle button always has both \`aria-expanded\` and \`aria-controls\` correctly tied to the dynamic \`id\` of the content container.
