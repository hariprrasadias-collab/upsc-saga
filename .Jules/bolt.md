# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2024-07-04 - Eliminate N+1 COUNT(*) queries in Boss Arena selection
**Learning:** Generating the list of available bosses in the Arena resulted in multiple N+1 `COUNT(*)` queries (one per distinct year and subject), unnecessarily slowing down the request. SQLite processes a single `GROUP BY` with `COUNT(*)` significantly faster than looping over elements to run individual `COUNT(*)` queries.
**Action:** Pre-aggregate counts using a `GROUP BY` query (e.g., `SELECT year, COUNT(*) FROM pyq_questions GROUP BY year`) and pass the pre-calculated count to the formatting function instead of letting it execute isolated DB calls.
