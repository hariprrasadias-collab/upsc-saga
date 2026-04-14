# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-03-03 - [Optimized arena boss listing to eliminate N+1 queries]
**Learning:** The `get_available_bosses` route fetched a list of distinct years and subjects, and then executed a separate `COUNT(*)` query for each in `get_boss_stats`. This resulted in N+1 queries when building the boss lists.
**Action:** Group iterative queries using `GROUP BY` to fetch counts in a single database round trip, and pass the count as a `precomputed_count` argument to helper functions to avoid redundant queries.
