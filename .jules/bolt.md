## 2026-01-31 - Build Failure Recovery
**Learning:** `tsc -b` (TypeScript Build) in CI/CD enforces strict type checking and unused variable checks (`noUnusedLocals`). Local `vite` dev server might be more lenient. Always run `pnpm build` locally before submitting to catch these.
**Action:** When fixing deployment failures, ensure to fix all `tsc` errors, including unused variables and type mismatches in third-party libraries (like Recharts formatters), even if they are pre-existing, as they block the entire build.
