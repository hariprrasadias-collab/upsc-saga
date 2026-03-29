# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2026-03-29 - [Fixed N+1 queries in mock_tests insertions and updates]
**Learning:** The `create_test` and `grade_test_attempt` routes in `backend/app/routes/mock_tests.py` originally iterated through test questions, executing a distinct `INSERT` or `UPDATE` SQL query for each question individually. In a scenario with 100 questions, this resulted in 100+ separate database calls, creating significant N+1 latency overhead.
**Action:** Use Python sqlite3's `conn.executemany()` function to perform batch database insertions and updates. Building a list of parameter tuples within loops and executing a single database call dramatically reduces database interaction overhead for multi-record operations.
