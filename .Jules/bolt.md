# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2024-07-07 - Strict TS Build Failure Fix
**Learning:** Render deployments use `NODE_ENV=production` by default which triggers stricter TypeScript compilation. Unused variables like `isUpscale` in `VisualPromptRenderer.tsx` cause `TS6133` build failures on Render.
**Action:** Prefix unused variables with an underscore (e.g., `_isUpscale`) to bypass the check while keeping the function signature intact.
## 2024-07-07 - Package Manager Hygiene
**Learning:** Hardcoding `npm install` inside `package.json` scripts (`"build": "npm install && tsc -b && vite build"`) causes CI pipeline failures and lockfile corruption in repositories strictly using `pnpm`.
**Action:** Always ensure nested `package.json` build scripts rely exclusively on the correct package manager (or remove the install step to let the root CI handle it) to avoid conflicting lockfiles (`package-lock.json` vs `pnpm-lock.yaml`).
