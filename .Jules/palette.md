## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2026-03-16 - [Adding ARIA Labels to Modal Close Buttons]
**Learning:** Icon-only interactive elements, such as standard modal close buttons using symbols like '×' or '✕', must always include an appropriate `aria-label` (e.g., `aria-label="Close"`) to ensure screen reader accessibility. Additionally, wrapping the symbol in `<span aria-hidden="true">`, prevents screen readers from reading out the symbol itself, enhancing clarity.
**Action:** Add `aria-label="Close"` to all modal close buttons that only use symbols and ensure the symbol is wrapped in `<span aria-hidden="true">`. When using `<span>` elements as buttons, ensure they have `role="button"`, `tabIndex={0}`, and an `onKeyDown` handler for keyboard accessibility.
