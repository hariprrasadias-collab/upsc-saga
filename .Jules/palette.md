## 2024-05-24 - Accessible Modal Dialogs and Close Buttons
**Learning:** Custom modals must explicitly declare `role="dialog"` and `aria-modal="true"` to trap screen reader focus properly, while icon-only close buttons (like '×') require an `aria-label` on the button and `aria-hidden="true"` on the visual icon to prevent confusing character readings.
**Action:** Always wrap visual icons in `aria-hidden="true"` spans inside buttons, and ensure modal containers have proper ARIA dialog attributes referencing their heading via `aria-labelledby`.
## 2024-05-24 - LightningCSS Keyframes Compilations
**Learning:** Vite's LightningCSS minifier throws `SyntaxError: [lightningcss minify] Unknown at rule: @keyframes` during production builds (`NODE_ENV=production pnpm run build`) if `@keyframes` are nested inside other CSS selectors or media queries. This strictness causes deployment failures on platforms like Render.
**Action:** Always define `@keyframes` at the top level of the CSS file, and never nest them inside other selectors or media queries. Before submitting UX CSS changes, always verify with a production build.
