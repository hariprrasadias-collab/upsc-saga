# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2026-04-10 - [Fixed N+1 Queries in Arena Bosses Fetching]
**Learning:** The `get_available_bosses` route iterated through arrays of unique years and subjects, executing a separate `SELECT COUNT(*)` query for every individual item. This created a classic N+1 query problem that severely delayed the endpoint as the dataset grew.
**Action:** Replaced iterative counting loops with a single `SELECT ... GROUP BY` query that handles all counts at once. When encountering `N` separate scalar queries triggered in a loop, always look to aggregate them into a single `GROUP BY` or `IN ()` clause.
