# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2024-05-23 - Strict TypeScript Errors on Render Deployment
**Learning:** During Render deployments, `NODE_ENV=production npm run build` enforces strict TypeScript compilation. This catches errors that might be ignored during local development (like TS6133 unused variables or TS2322 mismatched parameter types in library components like Recharts `Tooltip` formatters). Also, using `npm ci` on Render with a missing or conflicting `package-lock.json` vs `pnpm-lock.yaml` will cause the deployment to fail.
**Action:** Always verify builds locally with `NODE_ENV=production npm run build` before pushing. Fix TS errors by prefixing unused variables with `_` and typing problematic callback parameters (like Recharts formatters) as `any`. Always resolve lockfile conflicts.
