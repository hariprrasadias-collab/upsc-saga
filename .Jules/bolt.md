# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2024-05-18 - Fix N+1 queries in get_available_bosses using GROUP BY
**Learning:** Found an N+1 query issue in `backend/app/routes/arena.py` when generating boss stats. Looping over individual items and querying for `COUNT(*)` creates significant database overhead, especially on SQLite.
**Action:** Replace `SELECT DISTINCT` with `SELECT ..., COUNT(*) as count ... GROUP BY ...` in batch queries and pass the aggregated count directly down to the helper function. This eliminates all the repeated `COUNT(*)` DB requests in the loop.
