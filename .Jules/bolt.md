# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-03-03 - [Optimized get_time_distribution query aggregation]
**Learning:** `UNION ALL` across large tables to fetch raw data rows into Python memory for counting creates an O(N) memory and data-transfer bottleneck.
**Action:** When counting or aggregating combined records from multiple tables with `UNION ALL`, wrap the `UNION ALL` query in a subquery and apply a SQL `GROUP BY` clause. This shifts the aggregation workload to the database, converting an O(N) memory bottleneck into an O(M) one (where M is the bounded number of group keys).
