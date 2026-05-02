## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.
## 2024-05-23 - Emoji Accessibility in Icon-Only Buttons
**Learning:** When implementing icon-only buttons containing emojis (like ✏️ or 🗑️), screen readers may read the literal emoji names (e.g., "pencil emoji", "wastebasket emoji") out loud, even if an explicit `aria-label` is provided, causing redundant or confusing audio output.
**Action:** Always wrap the emoji in a `<span aria-hidden="true">` element and provide a descriptive `aria-label` on the parent `<button>`.
