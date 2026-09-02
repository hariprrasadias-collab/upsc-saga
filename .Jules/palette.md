## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2024-05-23 - Interactive Div Accessibility
**Learning:** Adding `onClick` handlers to `div` elements makes them interactive for mouse users but completely inaccessible to keyboard users (who rely on Tab) and screen readers (which rely on roles).
**Action:** When a semantic `<button>` cannot be used, always add `role="button"`, `tabIndex={0}`, and an `onKeyDown` handler supporting both 'Enter' and 'Space' (using `e.preventDefault()` for Space to prevent page scrolling) to custom interactive elements like cards.
## 2024-05-23 - Recharts TypeScript Types
**Learning:** Recharts Tooltip formatter functions often have highly strict and complex type definitions that fail strict TS compilation. Changing the type from `string | undefined` to `any` for arguments usually fixes these.
**Action:** Always check type signatures when fixing TS errors inside charting libraries like Recharts, and use `any` if the actual runtime arguments don't strictly adhere to the complex typings.
