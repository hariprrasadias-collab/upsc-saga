## 2024-05-21 - Sidebar Navigation Accessibility
**Learning:** The main navigation uses clickable `div` elements, completely locking out keyboard and screen reader users. This is a common pattern in dashboard UIs that must be actively refactored.
**Action:** Refactor to semantic `<button>` elements, ensuring `width: 100%` and `text-align: left` are applied to match block-level `div` behavior, and add clear `:focus-visible` styles.

## 2024-05-22 - Command Palette Accessibility
**Learning:** Overlays like Command Palettes often lack semantic structure, leaving screen reader users lost in a sea of divs. Adding `role="combobox"` and `aria-activedescendant` instantly transforms a confusing list into a navigable interface.
**Action:** Always wrap search-driven interfaces in `role="combobox"`/`listbox` pattern and ensure `aria-activedescendant` is updated with keyboard navigation.

## 2024-06-19 - Toast Notifications & Live Regions
**Learning:** Toast notifications often default to generic `div`s, which screen readers ignore completely. Using `role="alert"` (with `aria-live="assertive"`) for errors and `role="status"` (with `aria-live="polite"`) for info/success is critical for non-visual feedback.
**Action:** Always map notification types to appropriate ARIA roles and ensure close buttons have explicit `aria-label`s.
