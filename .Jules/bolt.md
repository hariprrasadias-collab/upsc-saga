# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-03-03 - [Arena Boss Stats N+1 Queries Fix]
**Learning:** In `backend/app/routes/arena.py`, `get_available_bosses()` fetched a list of unique subjects and years, and then called `get_boss_stats()` for each in a loop, running a `COUNT(*)` database query for every item. This created a severe N+1 query bottleneck as the number of years and subjects increased.
**Action:** When populating multiple stats that each require aggregation, avoid N+1 queries by leveraging `GROUP BY` SQL clauses to aggregate counts in a single query and map them into the results.
