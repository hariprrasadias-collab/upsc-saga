## 2024-05-21 - Sidebar Navigation Accessibility
**Learning:** The main navigation uses clickable `div` elements, completely locking out keyboard and screen reader users. This is a common pattern in dashboard UIs that must be actively refactored.
**Action:** Refactor to semantic `<button>` elements, ensuring `width: 100%` and `text-align: left` are applied to match block-level `div` behavior, and add clear `:focus-visible` styles.

## 2024-05-22 - Command Palette Accessibility
**Learning:** Overlays like Command Palettes often lack semantic structure, leaving screen reader users lost in a sea of divs. Adding `role="combobox"` and `aria-activedescendant` instantly transforms a confusing list into a navigable interface.
**Action:** Always wrap search-driven interfaces in `role="combobox"`/`listbox` pattern and ensure `aria-activedescendant` is updated with keyboard navigation.

## 2024-05-23 - Custom Modal Accessibility
**Learning:** Custom full-screen overlays often miss the semantic structure of dialogs. Screen readers perceive them as part of the normal document flow unless `role="dialog"` and `aria-modal="true"` are used, and focus is often not trapped.
**Action:** Enhance custom modals with `role="dialog"`, trap focus or focus initial container on mount, and always implement Escape key listeners for standard dismissal.
