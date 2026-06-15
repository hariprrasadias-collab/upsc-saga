# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-03-03 - [Arena Bosses N+1 Optimization]
**Learning:** Generating dynamic frontend components (like Boss lists) that require counting associated child records (like pyq_questions) will trigger N+1 queries if the counting logic remains isolated inside a component factory function called in a loop.
**Action:** Prefetch grouped counts (via `GROUP BY`) at the top level and pass the counts down into the factory function to avoid repeated database hits.

## 2025-03-03 - [Strict TypeScript & Deployment]
**Learning:** During Render deployments, if unused variables are left in the frontend TypeScript files, strict typing via `tsc -b` will fail with an error (`TS6133`). Prefixing unused parameters with an underscore (`_`) bypasses these compilation blocks.
**Action:** Always ensure code successfully builds with `tsc -b` and `vite build` prior to submission.
