## 2024-05-23 - Toast Notification Accessibility
**Learning:** Notifications are often invisible to screen readers without proper roles. Using `role="alert"` for errors (assertive) and `role="status"` for info (polite) ensures users are notified at the right urgency level.
**Action:** Always categorize toast notifications by urgency and apply corresponding `aria-live` regions, while ensuring close buttons have clear labels.

## 2024-05-23 - Anki Flashcard Accessibility
**Learning:** Flashcards require explicit keyboard handling (`onKeyDown` for Space/Enter) and `tabIndex="0"` on the card container to be accessible. Answer buttons should also have keyboard shortcuts (`aria-keyshortcuts`) matching power-user expectations (1, 2, 3, 4).
**Action:** Always implement keyboard listeners for custom interactive components like flashcards, and communicate shortcuts via ARIA attributes.
