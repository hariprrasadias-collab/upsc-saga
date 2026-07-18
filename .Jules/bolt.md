# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-02-18 - Replacing N+1 queries with bulk operations
**Learning:** In the analytics dashboard, retrieving performance metrics sequentially for multiple subjects (e.g. through a loop) creates unnecessary database round trips, which severely slows down endpoint response times (the N+1 query problem).
**Action:** Use batch aggregation with SQL `IN` clauses instead of individual queries when aggregating multiple items, while ensuring that the batch fallback properly defaults missing data arrays.
