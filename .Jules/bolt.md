# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2026-10-10 - [Optimize React array aggregations inside render loops]
**Learning:** The 'StudyPlanDashboard' component repeatedly computed `activePlan.flatMap(d => d.slots)` and used multiple `.reduce()` loops inside its `renderContent` function, resulting in O(N^2) time complexity per render.
**Action:** Use a `useMemo` hook to calculate necessary aggregations (`totalTasks`, `completedTasks`, `subjectStats`) in a single pass O(N) iteration, generating a dictionary map for O(1) lookups during the render phase.
