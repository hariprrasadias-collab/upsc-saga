# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2026-10-07 - React O(N*M) Render Blocking Mitigation
**Learning:** In React components that render lists, executing array aggregations like `.flatMap().filter()` inside a `.map` render loop results in O(N*M) time complexity during every single re-render. In StudyPlanDashboard, this caused massive lag.
**Action:** Always precompute map or record-based dictionaries using `useMemo` outside of the render return block to eliminate redundant O(N) sweeps. Look for `flatMap().filter()` calls hidden inside UI maps.
