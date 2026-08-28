# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-03-03 - [Optimized time distribution heatmap query to shift aggregation to DB]
**Learning:** The `get_time_distribution` API was pulling every single un-aggregated activity row across all dates into memory via `UNION ALL`, forcing Python to loop through thousands of dates sequentially to build the counts, creating an O(N) memory/data-transfer bottleneck.
**Action:** When aggregating or counting records combined from multiple tables via `UNION ALL`, wrap the `UNION ALL` statements in an outer subquery and apply a SQL `GROUP BY` clause (e.g. `SELECT date, COUNT(*) as count FROM (...) GROUP BY date`) to push the aggregation workload directly into the database engine.
