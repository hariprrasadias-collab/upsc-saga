## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-05-23 - Icon-Only Button Accessibility Pattern (The Scribe)
**Learning:** Icon-only close buttons (like `×` characters without text) are inherently inaccessible, as screen readers will announce confusing symbols like "multiply" or "times". Applying an `aria-label` to the `<button>` helps, but does not prevent the screen reader from also reading the text node `×` inside.
**Action:** When creating icon-only buttons with text characters or emojis, wrap the visible character in a `<span aria-hidden="true">` and provide a descriptive `aria-label` on the parent `<button>`. This forces the screen reader to *only* read the descriptive label and ignore the symbol.
