## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2026-04-20 - Adding ARIA Labels to Pomodoro Timer Controls
**Learning:** Standard `title` attributes on icon-only timer control buttons are insufficient for screen readers; `aria-label` attributes must be explicitly declared for accessibility.
**Action:** Add `aria-label` alongside or instead of `title` on all icon-only interactive UI components, specially floating controls like timers.

## 2026-04-20 - Fixing Render Build & Package Manager Conflicts
**Learning:** When fixing build scripts for Render, ensure no duplicated `scripts` JSON blocks exist in `package.json`. Furthermore, to enforce strict `pnpm` usage and prevent CI/CD failures, always delete `package-lock.json` if it exists alongside `pnpm-lock.yaml` or when updating root build scripts to use `pnpm` exclusively.
**Action:** Verify `package.json` structure carefully and ensure consistent package manager usage (`pnpm` only) to avoid Render failing to locate the `dist` directory or triggering strict-install conflicts.
