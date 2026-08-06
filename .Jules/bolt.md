# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2025-03-03 - [Optimized UNION ALL memory bottleneck via DB-level grouping]
**Learning:** When aggregating records combined from multiple tables using `UNION ALL` (e.g., retrieving activity dates in `get_time_distribution`), fetching all raw rows to Python results in O(N) memory and data transfer bottlenecks.
**Action:** Wrap the `UNION ALL` queries in a subquery and apply a SQL `GROUP BY` clause (e.g., `SELECT date, COUNT(*) FROM (...) GROUP BY date`) to shift the aggregation workload to the database and reduce memory overhead to O(1) per distinct group.
