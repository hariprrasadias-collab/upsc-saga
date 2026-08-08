# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2024-05-18 - [Resolve N+1 Queries in Analytics]
**Learning:** To resolve N+1 query performance bottlenecks when an endpoint iterates over distinct items to calculate statistics, execute a single SQL `GROUP BY` query to fetch all aggregates at once.
**Action:** Replace inner-loop queries with a single bulk SQL `GROUP BY` query executed beforehand, and map the results into a list or dictionary for O(1) lookups during the loop, shifting the aggregation workload to the database.
