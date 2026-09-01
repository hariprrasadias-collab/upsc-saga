# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-03-03 - [Optimized get_year_trends to eliminate N+1 queries]
**Learning:** The `get_year_trends` function in `backend/app/routes/seer.py` executed a `SELECT subject, COUNT(*) ... WHERE year = ?` query inside a loop for each year. This N+1 query pattern degraded performance as the number of years grew. It can be avoided by grouping the data by year and subject in a single query.
**Action:** Replace iterative database calls within loops with a single query using `GROUP BY` and transform the data in-memory to match the required format. This reduces the number of database queries from O(N) to O(1).
