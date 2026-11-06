# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-03-03 - [Optimized seer trends endpoint to eliminate N+1 queries]
**Learning:** The `get_year_trends` function in `backend/app/routes/seer.py` previously executed a `SELECT subject, COUNT(*) FROM pyq_questions WHERE year = ? GROUP BY subject` query inside a loop for each unique year to fetch the counts for that year, leading to an N+1 query problem that scales poorly with the number of years.
**Action:** Replace multiple looping database queries with a single bulk extraction query (e.g., `SELECT year, subject, COUNT(*) FROM pyq_questions GROUP BY year, subject`) when building data aggregates that split by multiple columns. Assemble the resulting map in memory instead of executing separate database accesses.
