## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2026-08-23 - LightningCSS rejects nested keyframes
**Learning:** Vite's CSS processing (using `lightningcss`) strictly rejects nested `@keyframes` rules (e.g., `@keyframes` defined inside another CSS selector or block), causing the build to fail with `SyntaxError: [lightningcss minify] Unknown at rule: @keyframes` during the `css-post` step.
**Action:** Always ensure `@keyframes` definitions are placed at the root level of the CSS file and not inside other blocks.
