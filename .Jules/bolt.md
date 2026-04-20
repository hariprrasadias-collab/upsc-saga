# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-05-22 - [Optimized shadow duel test generation to eliminate N+1 queries]
**Learning:** The `generate_shadow_duel` function in `backend/app/services/doppelganger_service.py` iteratively executed single database `INSERT` queries for each trap question via `conn.execute()` in a for-loop.
**Action:** When inserting multiple rows into a SQLite table in Python, construct a list of tuples containing the row data and execute a single `conn.executemany()` operation. This converts an O(N) database insertion process into a fast O(1) bulk operation, mitigating I/O context-switching overhead.
