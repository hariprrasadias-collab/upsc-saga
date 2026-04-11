# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2024-04-11 - [Optimized Seer XP history to eliminate N+1 queries]
**Learning:** The `consult_the_seer` function in `backend/app/routes/seer.py` iterated 7 times to sum `tasks` XP rewards for the last 7 days, executing 7 separate `SELECT SUM(xp_reward)` queries (an N+1 query bottleneck). Because we were looking for an aggregate sum within a bounded range of dates, these iterative queries were inefficient.
**Action:** Replace multiple date-specific queries with a single query bounded by a date range (`WHERE due_date >= ? AND due_date <= ?`), calculating the sums using `GROUP BY due_date`, and grouping the results in a local Python dictionary for O(1) lookups. This transforms an O(N) database query scenario into O(1) and reduces database connection overhead.
