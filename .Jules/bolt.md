# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-03-03 - [Optimized mock_tests endpoints to eliminate N+1 queries]
**Learning:** The `submit_attempt` and `create_test` functions in `backend/app/routes/mock_tests.py` iteratively executed database `UPDATE` and `INSERT` queries within a `for` loop for every question in a test. For tests with many questions (e.g., 100 questions), this created an O(N) "N+1 query" bottleneck, drastically increasing database roundtrips and latency.
**Action:** When performing bulk writes (updates or inserts) across multiple rows, gather the target data tuples into lists and utilize SQLite's `executemany()` to batch the operations into a single query.
