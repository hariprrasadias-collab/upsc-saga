## 2024-05-24 - Accessible Modal Dialogs and Close Buttons
**Learning:** Custom modals must explicitly declare `role="dialog"` and `aria-modal="true"` to trap screen reader focus properly, while icon-only close buttons (like '×') require an `aria-label` on the button and `aria-hidden="true"` on the visual icon to prevent confusing character readings.
**Action:** Always wrap visual icons in `aria-hidden="true"` spans inside buttons, and ensure modal containers have proper ARIA dialog attributes referencing their heading via `aria-labelledby`.
