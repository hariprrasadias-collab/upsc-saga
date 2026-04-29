# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2024-05-22 - [Eliminated N+1 query loop when fetching yearly subject distributions]
**Learning:** The `get_year_trends` function in `backend/app/routes/seer.py` iterated over each distinct year and executed a separate `SELECT COUNT(*)` query to get the subject distribution for that year. This N+1 query pattern creates significant database latency when the number of years grows.
**Action:** Always prefer fetching aggregated groupings in a single query using `GROUP BY` and doing the sorting/filtering in memory, instead of executing iterative database queries in a loop.
