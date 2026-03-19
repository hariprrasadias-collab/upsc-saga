# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-03-03 - [Arena Boss N+1 Query Elimination]
**Learning:** In the `/bosses` endpoint, the `get_available_bosses()` function fetched a list of unique 'years' and 'subjects' and passed them iteratively to `get_boss_stats()`. For each year or subject passed, `get_boss_stats` executed a `SELECT COUNT(*)` database query, creating a massive N+1 query performance bottleneck as distinct properties multiplied.
**Action:** When gathering metrics for a broad list of categories, eliminate iteration-based database queries by refactoring the initial broad selection into `SELECT ... COUNT(*) ... GROUP BY ...`. Pass the grouped results into helper functions as `precomputed` variables to skip redundant downstream DB queries.
