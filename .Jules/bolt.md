# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2024-03-17 - N+1 Query Loops in Python Groupings
**Learning:** Found N+1 query loops occurring within Python iterations inside analytic endpoints (`consult_the_seer` looping 7 days with queries, `get_year_trends` looping years and fetching subjects counts). Executing multiple SQL loops slows down request handling sequentially.
**Action:** Replace `for` loop database lookups with a single large aggregated `GROUP BY` query. Once fetched, use Python `collections.defaultdict` and dictionary mapping to efficiently group and populate the desired nested JSON shape.
