# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-05-17 - [Optimized arena bosses API to eliminate N+1 queries]
**Learning:** The `get_available_bosses` function in `backend/app/routes/arena.py` was fetching all distinct years and subjects, then running a `SELECT COUNT(*)` query individually for each one via `get_boss_stats()`. This classic N+1 query pattern degraded performance as the dataset grew.
**Action:** Always identify opportunities to replace iterative individual database counts with batched `GROUP BY` SQL aggregation queries. Passing a precalculated count default to existing logic safely neutralizes the N+1 bottleneck without breaking downstream dependencies.
