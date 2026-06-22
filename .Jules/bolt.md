# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-03-03 - Optimize mock test scoring to eliminate N+1 database updates
**Learning:** During test scoring in `submit_attempt`, updating each answer individually in a loop leads to an N+1 database bottleneck.
**Action:** Prevent N+1 bottlenecks during batch database updates by lifting the `UPDATE` logic out of loops. Accumulate target parameters into lists during iteration and execute a single `conn.executemany()` statement outside the loop.
