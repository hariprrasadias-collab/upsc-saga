# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2024-07-22 - Refactored N+1 query in subject analytics
**Learning:** When fetching subject performance for a list of subjects, calling a function that performs 3 individual SQL queries inside a loop creates an N+1 performance bottleneck.
**Action:** Lift the database logic out of the loop and use an `IN` clause to query all subjects in a single batch query for each table. Iterate over the results to map them back to the original subjects.
