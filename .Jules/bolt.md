# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2024-06-03 - [Optimized Seer XP history query to eliminate N+1 queries]
**Learning:** The `get_seer_stats` function in `backend/app/routes/seer.py` iteratively fetched `tasks` data `7` times (via `SELECT SUM(xp_reward)`) inside a loop over the last 7 days. Because each query opened a database operation, this was an O(N) operation that added unnecessary overhead.
**Action:** Lift repeated logic out of loops by using a single query with a `BETWEEN` date range and `GROUP BY`, transforming the O(N) database query scenario into O(1).
