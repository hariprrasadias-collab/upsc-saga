## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2024-06-17 - Custom Modal Accessibility
**Learning:** Custom modal implementations frequently lack standard WAI-ARIA modal attributes (`role="dialog"`, `aria-modal="true"`, and `aria-labelledby`), which makes them inaccessible to screen readers. In addition, visible close indicators (like `×` characters) should always be hidden from screen readers using `aria-hidden="true"` and replaced with an explicit `aria-label` to provide clearer context.
**Action:** When implementing or reviewing custom modal dialogues, ensure they include `role="dialog"`, `aria-modal="true"`, and an `aria-labelledby` linking to their heading. Always wrap visual "X" close buttons in `aria-hidden="true"` spans and provide an `aria-label` on the button itself.
