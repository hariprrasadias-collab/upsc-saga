# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2026-05-20 - [Optimized seer queries to eliminate N+1 database calls]
**Learning:** In backend routes like `consult_the_seer` and `get_year_trends`, looping over date ranges or distinct items (like years) and making individual database queries inside the loop can introduce N+1 query problems.
**Action:** Lift repeated query logic out of the loops by using `GROUP BY` and `BETWEEN` or composite groupings (`GROUP BY year, subject`) to fetch all the necessary aggregated data in a single SQL call, then correlate it locally in Python using dictionaries.
