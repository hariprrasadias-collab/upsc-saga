# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2024-09-14 - Optimize Render Loops with O(1) Lookups
**Learning:** Inline array operations like `.filter().reduce()` inside a component function (e.g., `getProgress`) cause redundant O(N) calculations every time the component renders or a mapping loop calls them.
**Action:** Always pre-calculate aggregated list metrics into a dictionary/map inside a `useMemo` block, allowing the render loop to perform instantaneous O(1) lookups instead of re-evaluating the data.
