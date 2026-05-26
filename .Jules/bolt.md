# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2024-05-26 - [Optimized get_year_trends to eliminate N+1 queries]
**Learning:** The `get_year_trends` function in `backend/app/routes/seer.py` iterated over distinct years, making an individual SQL query for each year to get subject distributions. This structure caused an N+1 query problem, slowing down execution as the number of years grew.
**Action:** Replace the iterative year-based queries with a single query using `GROUP BY year, subject` and compile the data structure efficiently using a dictionary hash map lookup.
