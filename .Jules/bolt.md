# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2025-03-04 - [Eliminated N+1 query in Arena Bosses Endpoint]
**Learning:** Returning list of records (like boss years and subjects) from distinct values and looping over each element to fetch related aggregates (using `COUNT(*)`) creates a critical N+1 query performance bottleneck during serialization. In SQLite, fetching a single aggregated resultset for all data in a single table avoids the overhead of executing O(N) trip delays for each loop iteration.
**Action:** When creating APIs that loop through distinct data values and calculate statistics dynamically per item, proactively query those items using `GROUP BY` and passing aggregates downwards rather than pulling statistics per iteration loop.
