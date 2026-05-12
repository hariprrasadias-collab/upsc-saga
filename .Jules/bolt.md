# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2026-05-11 - [Optimized get_year_trends endpoint]
**Learning:** Sequential queries within loops inside endpoints (N+1 query pattern) severely degrade backend response times as the dataset scales. In `backend/app/routes/seer.py`, querying subject counts iteratively for each year was an O(N) operation.
**Action:** Always prefer single, aggregated database queries (e.g., using `GROUP BY`) over executing `SELECT` queries inside Python `for` loops, mapping the results in memory to transform O(N) database calls into O(1).
