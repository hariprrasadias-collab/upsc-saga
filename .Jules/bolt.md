# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-03-03 - [Optimized SQLite inserts by using executemany to prevent N+1 bottlenecks]
**Learning:** Sequential `conn.execute()` queries within `for` loops inside backend routes (e.g. `mock_tests.py` and `pyq.py`) for creating tests or recording quiz answers create N+1 query bottlenecks and noticeable latency when datasets are large.
**Action:** Always accumulate SQLite row parameters into list comprehensions or tuples and batch execute them via `conn.executemany()` instead of iterating inserts directly inside standard python for-loops.
