# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2025-02-14 - Memoized Array Operations in React Rendering Loop
**Learning:** Found an instance in `SyllabusTracker.tsx` where an expensive O(N) array `.filter().reduce()` operation was nested inside a function (`getProgress`) that was invoked multiple times per render cycle (3 times for each paper rendered). This causes an exponential number of redundant calculations during each component render cycle.
**Action:** Always wrap expensive inline computation dependencies, like calculating aggregated states from arrays, in `useMemo` blocks and extract them to O(1) dictionary lookups during render cycles to prevent unnecessary runtime overhead.
