# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2024-05-18 - [Optimization of StudyPlanDashboard]
**Learning:** The React application recalculates activePlan statistics (like subject counts) multiple times across different viewModes by re-running `.flatMap().filter()` on a potentially large array of study slots within the render loop.
**Action:** When a React component repeatedly executes expensive array operations within render loops for multiple rendered elements, move the computation into a `useMemo` hook that generates an O(1) dictionary lookup map (e.g., `Record<string, {total: number, completed: number}>`) to eliminate redundant O(N) overhead.
