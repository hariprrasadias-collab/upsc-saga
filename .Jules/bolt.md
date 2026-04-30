# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2024-05-23 - [Optimized arena bosses API to eliminate N+1 queries]
**Learning:** The `get_available_bosses` endpoint in `backend/app/routes/arena.py` suffered from an N+1 query issue. It iterated over every distinct year and subject, running individual `SELECT COUNT(*)` queries inside `get_boss_stats()` to build the list.
**Action:** Always fetch bulk aggregated counts using `GROUP BY` rather than relying on looped individual fetch operations. This turned O(N) queries into O(1), dropping the queries per API call from ~85 down to 3.
