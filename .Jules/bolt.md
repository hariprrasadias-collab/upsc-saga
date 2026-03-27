# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2024-03-24 - N+1 Query Fixes in `get_year_trends` and `consult_the_seer`
**Learning:** Replaced iterative loop-based queries (N+1 queries) fetching data across multiple elements with single `GROUP BY` bulk queries to significantly improve database performance and reduce latency.
**Action:** When calculating statistics across multiple distinct metrics (e.g., years, days), utilize bulk SQL queries with `GROUP BY` and then transform the results in Python memory rather than repeatedly querying the database inside a loop.
