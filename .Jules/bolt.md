# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-03-03 - [Optimized Arena bosses query to eliminate N+1 latency]
**Learning:** The `get_available_bosses` function in `backend/app/routes/arena.py` was iteratively running a `SELECT COUNT(*)` for every distinct year and subject, causing severe N+1 database querying bottlenecks as data grows.
**Action:** Transformed the database interaction by replacing the iterative `COUNT(*)` queries with bulk `GROUP BY year` and `GROUP BY subject` aggregations. This successfully converts the queries from O(N) complexity back to O(1).
