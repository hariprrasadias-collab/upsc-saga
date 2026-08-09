# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-05-18 - [Optimized UNION ALL query with subquery aggregation]
**Learning:** When retrieving records combined from multiple tables via `UNION ALL` just to count or aggregate them in Python, it creates O(N) memory usage and data transfer overhead.
**Action:** Wrap the `UNION ALL` queries in a subquery and apply a SQL `GROUP BY` and `COUNT(*)` clause to shift the aggregation workload to the database, eliminating the need for Python to fetch all the raw rows.
