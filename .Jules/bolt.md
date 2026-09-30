# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2026-09-29 - [Optimized Study Plan Dashboard by preventing O(N*M) subject iteration during render]
**Learning:** The `StudyPlanDashboard.tsx` performed repeated expensive `.flatMap()` and `.filter()` array operations for multiple subjects inside a conditional block within the component render logic. This resulted in O(N*M) complexity on every render loop when calculating the subject task breakdown.
**Action:** Extract repeating data aggregations out of render loops and map functions. Pre-calculate lookup dictionaries using `useMemo` hooked to the correct filtered data array dependency (e.g., `activePlan`) to achieve O(N) evaluation and drastically improve component rendering speed.
