# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-03-03 - [Optimized arena boss generation and analytics to eliminate N+1 queries]
**Learning:** Functions like `get_available_bosses` in `arena.py` and sequential date fetching in `analytics_service.py` frequently make database requests within a loop, generating N+1 queries and creating a large bottleneck. By adjusting helper functions (e.g., `get_boss_stats`) to accept pre-aggregated data (like `pre_count` and `pre_row`) from a single `GROUP BY` query, and by refactoring multiple date-fetching `SELECT` queries into a single `UNION ALL` query, we can drastically reduce the number of database queries.
**Action:** When a helper function performs a database read inside a loop, refactor it to accept optionally pre-fetched data. Pre-fetch the necessary counts or rows using `GROUP BY` before the loop. For gathering separate, disparate sets of similar data (like dates), use `UNION ALL` to accomplish it in a single query.
