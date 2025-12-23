## 2024-05-21 - Sidebar Navigation Accessibility
**Learning:** The main navigation uses clickable `div` elements, completely locking out keyboard and screen reader users. This is a common pattern in dashboard UIs that must be actively refactored.
**Action:** Refactor to semantic `<button>` elements, ensuring `width: 100%` and `text-align: left` are applied to match block-level `div` behavior, and add clear `:focus-visible` styles.

## 2024-05-22 - Command Palette Accessibility
**Learning:** Overlays like Command Palettes often lack semantic structure, leaving screen reader users lost in a sea of divs. Adding `role="combobox"` and `aria-activedescendant` instantly transforms a confusing list into a navigable interface.
**Action:** Always wrap search-driven interfaces in `role="combobox"`/`listbox` pattern and ensure `aria-activedescendant` is updated with keyboard navigation.

## 2025-12-23 - Toast Notifications
**Learning:** Visual-only toasts (divs) are invisible to screen readers, meaning critical errors or success confirmations are missed.
**Action:** Always assign `role="alert"` (for errors/warnings) or `role="status"` (for success/info) to toasts, and ensure the close button has an `aria-label`.
