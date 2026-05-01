# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-03-03 - [Replaced N+1 nested query with SQLite bare column feature]
**Learning:** SQLite's handling of `MAX()` with `GROUP BY` guarantees that unaggregated columns return values from the same row as the max value. Using nested `WHERE id IN (SELECT MAX(id) ...)` queries causes unnecessary O(n^2) nested loop performance.
**Action:** Use bare column selection (e.g. `SELECT *, MAX(id) as max_id ... GROUP BY metric_name`) instead of nested `IN` queries. Remember to `.pop('max_id', None)` from row dicts to avoid schema changes.
