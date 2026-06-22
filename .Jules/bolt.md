# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2024-05-19 - Use executemany for Bulk Inserts
**Learning:** In `backend/app/services/mock_test_service.py`, tests were generated using a standard loop with `conn.execute()` for each `INSERT`. This effectively executes $N$ database commit transactions sequentially, causing significant "N+1" overhead and latency inside the mock test generator routine.
**Action:** When performing bulk writes (like test questions or large logs), formulate a list comprehension of data parameters and strictly use `conn.executemany` which processes inserts in an optimized batched execution at O(1) commit overhead rather than O(n).
