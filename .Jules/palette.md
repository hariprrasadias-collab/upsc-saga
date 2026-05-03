## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-05-23 - Screen Reader Symbol Announcements
**Learning:** Screen readers often announce symbols like `×` as literal math terms (e.g., "multiply" or "times"), creating confusion for users who only need to know it's a "close" button.
**Action:** When adding `aria-label` to icon-only buttons containing text symbols or emojis, always wrap the symbol itself in a `<span aria-hidden="true">` to prevent the screen reader from reading both the semantic label and the literal symbol.
