# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-04-25 - [Optimized SQLite nested subquery to avoid N+1 query using bare columns feature]
**Learning:** The nested subquery `WHERE id IN (SELECT MAX(id) FROM table GROUP BY field)` leads to two queries (or poor index usage / temp B-TREE generation) and effectively acts as a potential O(N^2) bottleneck for larger datasets.
**Action:** Replace nested loops by a single `GROUP BY` using SQLite's "bare column" feature (`SELECT *, MAX(id) FROM table GROUP BY field`), which automatically selects the correct values corresponding to the MAX element without an explicit self-join.
