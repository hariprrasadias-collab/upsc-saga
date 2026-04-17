## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2026-04-17 - Icon-Only Button Accessibility in Interactive Widgets
**Learning:** Interactive widgets like timers and floating controls often use icon-only buttons (with tooltips/titles) to save space. Relying solely on `title` attributes is insufficient for screen reader accessibility; these elements require explicit `aria-label` attributes to convey their function clearly.
**Action:** When implementing icon-only buttons (e.g., settings, edit, minimize, save/cancel controls), always include an explicit `aria-label` attribute that clearly describes the action, regardless of whether a `title` tooltip exists.
