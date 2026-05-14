## 2024-05-23 - Toast Notification Accessibility
## 2026-05-11 - Accessible Icon-Only Modal Close Buttons
**Learning:** For modal close buttons that rely solely on visual cues like `&times;` or `×`, simply adding `aria-label="Close"` to the `<button>` is insufficient. Screen readers will often announce the visual character itself (e.g., "multiply" or "times") in addition to the label, causing confusion.
**Action:** When creating icon-only buttons with text-based symbols, always wrap the symbol in a `<span aria-hidden="true">` to hide the raw text character from assistive technologies while preserving the accessible `aria-label` on the parent button.
