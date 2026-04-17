# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2026-04-17 - [Use executemany for batch database inserts]
**Learning:** When generating multiple database rows dynamically (e.g., test questions or answers), executing `INSERT` inside a `for` loop causes substantial I/O overhead and performance bottlenecks. Each loop iteration triggers a separate database API boundary crossing and Python-to-C context switch in SQLite.
**Action:** Use Python's `sqlite3.Connection.executemany()` with pre-compiled tuples. This transforms O(N) database calls into O(1), yielding measurable performance boosts for batch operations like mock test creation.
