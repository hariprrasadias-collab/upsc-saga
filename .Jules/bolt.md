# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-03-03 - [Replaced N+1 INSERTs and UPDATEs with executemany in Python]
**Learning:** Iterative database queries for INSERTs or UPDATEs within Python loops (N+1 queries) are a common bottleneck. This was observed in `submit_attempt` and `create_test` functions in `backend/app/routes/mock_tests.py`.
**Action:** Replaced iterative `.execute()` calls within loops with a single `.executemany()` call by building a list of tuples with parameters. This significantly reduces database roundtrips and optimizes performance. Also ensures that fields remain consistent with the original schema logic when applying the optimization.
