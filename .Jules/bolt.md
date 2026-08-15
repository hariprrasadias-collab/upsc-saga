# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2024-08-14 - Precomputing derived values in React renders
**Learning:** Performing multiple array operations (like `find`, `filter`, `reduce`) inside helper functions like `getProgress` that are invoked repeatedly during a render causes unnecessary O(N) operations.
**Action:** Memoize the aggregated results (e.g., using a `progressMap`) using `useMemo` so the values are computed only when the underlying state changes, changing O(N) operations inside render loops into O(1) lookups.
