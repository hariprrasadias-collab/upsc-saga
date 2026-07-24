## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2026-07-24 - Pomodoro Timer Accessibility
**Learning:** The `PomodoroTimer` component in this application had several icon-only buttons (like settings, minimize, history, and edit controls) that lacked screen-reader descriptions.
**Action:** Always ensure that any icon-only button used in custom interactive components is provided with an `aria-label` attribute describing its function.
## 2026-07-24 - Build Failure Resolution
**Learning:** In projects that enforce lockfile consistency (like Render's `npm ci` / `pnpm install --frozen-lockfile`), explicitly calling `npm install` within a `pnpm` workspace builds step leads to a conflicting `package-lock.json`. Additionally, strictly typed builds treat unused variables as fatal errors (`TS6133`).
**Action:** Always maintain strict package manager hygiene (e.g. use `pnpm` exclusively without mixing `npm` commands) and prefix any intentionally unused variables with an underscore to safely bypass TS checks without affecting logic.
