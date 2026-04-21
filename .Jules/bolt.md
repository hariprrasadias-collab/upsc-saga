# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2026-04-21 - strict TS compilation in react UI
**Learning:** When strict TS6133 failures occur due to unused params, verify if removing the param from the callback is safe, and remember to pass arguments accordingly.
**Action:** Run tsc -b locally to catch such issues.

## 2026-04-21 - Render root build script duplicate override
**Learning:** Duplicate keys in package.json (like two scripts objects) can silently override the correct build instructions. Render expects a dist folder at the root level for static site deployments depending on its configuration, and if the build script just runs in the frontend directory without copying to the root, Render will fail with 'Publish directory dist does not exist!'.
**Action:** Ensure package.json does not have duplicate keys and the build script properly copies frontend build output.
