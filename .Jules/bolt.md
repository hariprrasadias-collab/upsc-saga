# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2024-05-28 - Replace execute() in loops with executemany() for bulk inserts
**Learning:** SQLite in Python has a high overhead when executing individual `INSERT` statements inside a `for` loop. `cursor.execute` parses the query on each iteration. For bulk insertions, `cursor.executemany` is significantly faster as it prepares the statement once and executes the loop at the C level, thereby converting an N+1 database operations bottleneck into a single bulk database operation.
**Action:** When bulk inserting rows from a list (e.g., questions into mock tests or pyq quiz answers), accumulate the parameter tuples in a Python list and execute a single `conn.executemany(...)` instead of running `conn.execute(...)` inside a loop.
