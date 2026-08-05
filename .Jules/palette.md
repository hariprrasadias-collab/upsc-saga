## 2024-08-05 - Wrapping emojis in aria-hidden
**Learning:** When making UX improvements to icon-only buttons by adding `aria-label`, the inner visual element (e.g., emojis or symbols) must be wrapped in `<span aria-hidden="true">`. This prevents assistive technologies from redundantly reading the visual character's default name alongside the newly provided semantic label.
**Action:** Always include `<span aria-hidden="true">` around visual elements within icon-only buttons when adding `aria-label`s.
