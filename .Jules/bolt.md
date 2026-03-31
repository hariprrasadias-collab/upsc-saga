# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2024-05-17 - Bulk SQLite Inserts
**Learning:** In a SQLite-heavy Python backend, using an iterative `conn.execute('INSERT ...')` inside a loop introduces substantial N+1-like performance bottlenecks due to Python-to-C API transitions and repeated SQLite query parser overhead. This can severely slow down bulk generation tasks (like foresight predictions, creating mind palace artifacts, and generating quest records).
**Action:** When inserting multiple rows derived from an array, always aggregate the values into a list of tuples and use `conn.executemany(query, params)`. It offloads the loop to C and significantly speeds up persistence.
