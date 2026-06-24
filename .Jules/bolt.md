# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2025-06-24 - [Optimized submit_attempt to eliminate N+1 update query]
**Learning:** Performing `conn.execute` statements inside an iterative loop, especially during bulk processing like checking test answers in `backend/app/routes/mock_tests.py`'s `submit_attempt`, creates an N+1 performance bottleneck.
**Action:** Lift repeated logic out of loops. Accumulate the query parameters into lists during iteration and execute a single `conn.executemany()` statement outside the loop to execute database updates in batch.
