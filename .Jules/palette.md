## 2024-05-02 - Added `aria-label` to Close Buttons
**Learning:** React buttons containing only symbols like `×` are a common pattern for dismissible dialogs, but they are inaccessible to screen readers as they are visually-reliant.
**Action:** Always verify if a button has text content. If it relies purely on visual cues, ensure it has an `aria-label` to provide context (e.g., `aria-label="Close dialog"`).
