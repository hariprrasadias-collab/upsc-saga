## 2024-05-21 - Sidebar Navigation Accessibility
**Learning:** The main navigation uses clickable `div` elements, completely locking out keyboard and screen reader users. This is a common pattern in dashboard UIs that must be actively refactored.
**Action:** Refactor to semantic `<button>` elements, ensuring `width: 100%` and `text-align: left` are applied to match block-level `div` behavior, and add clear `:focus-visible` styles.

## 2024-05-22 - Command Palette Accessibility
**Learning:** Overlays like Command Palettes often lack semantic structure, leaving screen reader users lost in a sea of divs. Adding `role="combobox"` and `aria-activedescendant` instantly transforms a confusing list into a navigable interface.
**Action:** Always wrap search-driven interfaces in `role="combobox"`/`listbox` pattern and ensure `aria-activedescendant` is updated with keyboard navigation.

## 2024-06-18 - Toast Notification Accessibility
**Learning:** Toasts are dynamic updates that often go unnoticed by screen readers if they lack `role="alert"` or `aria-live` regions. Simply adding these attributes makes critical feedback instantly accessible.
**Action:** Ensure all toast notifications explicitly define `role="alert"` (for errors) or `role="status"` (for info), and use appropriate `aria-live` levels ("assertive" vs "polite").

## 2024-06-18 - Critical Error State Accessibility
**Learning:** Application-blocking error screens often default to unstyled text, leaving users stranded without context or recourse. Wrapping these in `role="alert"` and adding a clear "Retry" action transforms a dead end into a navigable recovery path.
**Action:** Always wrap full-screen error states in `role="alert"` with `aria-live="assertive"` and ensure at least one focusable action (like Retry or Home) is available.
