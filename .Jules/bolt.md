# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2024-05-23 - Optimize analyze_all_performance to eliminate N+1 queries
**Learning:** The `analyze_all_performance` function was causing an N+1 query issue by looping over all topics and issuing multiple database calls for each one (fetching stats, checking recent failures, and inserting/updating).
**Action:** Always group data in bulk using SQL features like `GROUP BY` and use `executemany` with a list of tuples to process bulk updates/inserts instead of doing them inside a loop.
