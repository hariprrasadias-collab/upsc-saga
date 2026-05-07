# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-05-07 - [Optimized get_year_trends to eliminate N+1 queries]
**Learning:** The `get_year_trends` function in `backend/app/routes/seer.py` previously executed an initial query to fetch years and then performed another query for each year to count subjects, causing an N+1 query problem.
**Action:** Replaced the loop with a single grouped query `SELECT year, subject, COUNT(*) as count FROM pyq_questions GROUP BY year, subject` and mapped it in memory. Always use `GROUP BY` with multiple columns for complex aggregation needs to avoid iterative database queries.
