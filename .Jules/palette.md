## 2025-03-14 - Accessible Icon-Only Close Buttons
**Learning:** The application uses bare Unicode multiplication/cross symbols (e.g., "✖", "✕") for modal close buttons rather than SVGs or font icons. Screen readers will confusingly read these out as "multiply" or "times" if not properly hidden.
**Action:** When creating icon-only close buttons using text symbols, always wrap the symbol in `<span aria-hidden="true">` and apply `aria-label="Close"` directly to the `<button>` element to ensure proper screen reader announcement.
