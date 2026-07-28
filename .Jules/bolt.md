# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2025-03-03 - [Optimized time distribution heatmap query]
**Learning:** The `get_time_distribution` function in `backend/app/routes/analytics.py` used a UNION ALL query to fetch every individual activity date into Python memory only to count them per day. This is an O(N) data transfer and memory bottleneck.
**Action:** Wrap the UNION ALL query in an outer query and use SQLite's `GROUP BY date, COUNT(*)` to shift the aggregation to the database, reducing the result set to O(D) where D is the number of distinct days.
