# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-03-03 - [Optimized /bosses endpoint to eliminate N+1 queries]
**Learning:** The `/bosses` endpoint in `backend/app/routes/arena.py` was fetching the distinct `year` and `subject` from `pyq_questions` and then executing a separate `SELECT COUNT(*)` query for each inside `get_boss_stats`. This resulted in N+1 queries (1 for the list + N for the counts).
**Action:** Replaced the distinct list queries with single `GROUP BY` queries that compute the counts simultaneously (`SELECT year, COUNT(*) as count FROM pyq_questions GROUP BY year`). The precomputed counts are then passed downstream to avoid iterative database lookups, transforming O(N) database operations to O(1).
