# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-03-04 - [Optimized repetitive rendering logic in StudyPlanDashboard]
**Learning:** In React components like `StudyPlanDashboard.tsx`, performing repetitive array computations (like `.flatMap().filter().length`) inside render loops for multiple elements (e.g., subject-by-subject mapping) causes redundant O(N) operations on every render.
**Action:** Extract expensive repetitive computations from the render loop using `useMemo` to construct an O(1) dictionary map (e.g., mapping subject names to task counts). Then, use simple property lookups inside the map during render.
