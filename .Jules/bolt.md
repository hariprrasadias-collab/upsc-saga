# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-03-03 - [Optimized mock test attempts and creation to eliminate N+1 queries]
**Learning:** In endpoints like `submit_attempt` and `create_test` (within `backend/app/routes/mock_tests.py`), executing `conn.execute()` sequentially inside a loop (whether to update answer correctness or insert new questions) results in significant N+1 latency, especially for tests with many questions.
**Action:** When handling bulk inserts or updates based on list/iterable data, accumulate the tuple parameters into a list and execute them via `conn.executemany()` to batch the database transaction into a single operation, transforming O(N) database trips into O(1).
