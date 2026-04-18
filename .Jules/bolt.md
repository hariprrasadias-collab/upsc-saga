# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-05-24 - [Optimized bulk database inserts by switching to executemany]
**Learning:** When generating tests with numerous questions in Python using SQLite, iterating through a loop to execute individual `INSERT` statements generates significant overhead due to consecutive disk I/O flushes. This bottleneck escalates quickly with test sizes.
**Action:** Utilize the `conn.executemany()` function with a list of tuples to process bulk database entries. This converts N sequential database transactions into a single operation, producing measurable performance gains (e.g., ~1.5x speedup for 1000 rows in test scenarios).
