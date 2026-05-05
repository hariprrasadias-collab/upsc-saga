# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-05-05 - Avoid N+1 queries by pre-aggregating with GROUP BY
**Learning:** The `/bosses` endpoint in `backend/app/routes/arena.py` was generating N+1 queries by iterating through distinct years and subjects and calling a counting query for each one.
**Action:** When calculating statistics across multiple categories (like counts for years and subjects), use a single SQL `GROUP BY` query beforehand. Pass the precalculated result into the downstream function using an optional parameter to gracefully skip the N+1 query overhead.
