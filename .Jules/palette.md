## 2024-08-05 - Wrapping emojis in aria-hidden
**Learning:** When making UX improvements to icon-only buttons by adding `aria-label`, the inner visual element (e.g., emojis or symbols) must be wrapped in `<span aria-hidden="true">`. This prevents assistive technologies from redundantly reading the visual character's default name alongside the newly provided semantic label.
**Action:** Always include `<span aria-hidden="true">` around visual elements within icon-only buttons when adding `aria-label`s.

## 2024-08-05 - Fixing TS6133 Deployment Blockers
**Learning:** Sometimes small UX/accessibility PRs (like adding aria-labels) get blocked in production build pipelines (like Render) due to strict TypeScript compilation errors on unrelated files, such as `TS6133` unused variable errors.
**Action:** When a strict TypeScript compiler error blocks deployment post-submission, permanently resolve it by implementing the fix in the codebase (e.g., prefixing unused variables with an underscore like `_isUpscale`) and commit the change, even if the error wasn't caused by the initial UX work.
