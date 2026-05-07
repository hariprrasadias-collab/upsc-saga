## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## $(date +%Y-%m-%d) - Toggle Button Accessibility
**Learning:** Filter buttons that toggle active states using only visual CSS classes (like `className="active"`) leave screen reader users unaware of the current filter.
**Action:** Always add `aria-pressed={isActive}` to toggle buttons to correctly announce their pressed/unpressed state to assistive technologies, and explicitly set `type="button"` to avoid default form submission behaviors.
