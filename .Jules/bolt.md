# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-03-03 - [Optimize N+1 query bottlenecks in batch database inserts]
**Learning:** In Python's sqlite3, running `conn.execute()` inside a loop for batch inserts causes N+1 query performance bottlenecks. `conn.executemany()` is a much faster O(1) alternative, but it doesn't return `lastrowid` for the inserted records.
**Action:** When IDs are needed after insertion (like in revision cards), construct a single `INSERT` query with multiple `VALUES` placeholders dynamically to maintain bulk insertion performance.
