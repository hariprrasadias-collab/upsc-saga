# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2024-07-11 - Bulk Insert Bottlenecks with SQLite
**Learning:** Performing database `execute` operations iteratively inside `for` loops causes N+1 query bottlenecks, significantly impacting performance during large operations like processing mock tests or generating artifacts.
**Action:** Always use `executemany` with a prepared list of tuples to batch operations into a single transaction when performing bulk inserts or updates in SQLite.
