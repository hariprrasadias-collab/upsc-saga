# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-04-29 - [Optimized year trends data to eliminate N+1 queries]
**Learning:** When aggregating nested data (e.g., questions per subject per year) for a frontend chart, doing a separate query per dimension (like querying for each year) causes an N+1 query bottleneck. Fetching the cross-product using `GROUP BY year, subject` and sorting the unique sets in-memory ensures both O(1) lookups and consistent JSON ordering for the frontend.
**Action:** Instead of querying within a loop for chart data, use multi-column `GROUP BY` to retrieve all metrics in a single query and assemble the required structure in Python.
