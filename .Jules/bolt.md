# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-03-03 - [Optimized heatmap activity aggregation to eliminate O(N) memory overhead]
**Learning:** The `get_time_distribution` function in `backend/app/routes/analytics.py` queried multiple tables using `UNION ALL` and aggregated the counts manually in Python. This resulted in pulling all rows into memory and transferring them over the database connection.
**Action:** To resolve O(N) memory and data transfer bottlenecks when counting or aggregating records combined from multiple tables using `UNION ALL`, wrap the `UNION ALL` queries in a subquery and apply a SQL `GROUP BY` clause (e.g., `SELECT date, COUNT(*) FROM (...) GROUP BY date`) to shift the aggregation workload to the database.
