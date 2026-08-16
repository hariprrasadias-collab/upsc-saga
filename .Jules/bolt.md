# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-03-04 - [Optimized time distribution heatmap endpoint to push aggregations to DB]
**Learning:** In the `get_time_distribution` endpoint within `backend/app/routes/analytics.py`, all activity records over a date range were fetched individually using `UNION ALL` across three tables, causing O(N) data transfer and memory usage, where N is the total number of activities.
**Action:** When aggregating or counting records across multiple tables with `UNION ALL`, wrap the queries in a subquery and apply `GROUP BY` to shift the aggregation load entirely to the database, preventing memory and data transfer bottlenecks.
