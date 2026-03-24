# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2026-03-24 - N+1 Query Optimization for Category Counts
**Learning:** Using a single `GROUP BY` query to fetch all category counts at once, passing the results downstream via `precomputed_count` kwargs, prevents N+1 query bottlenecks instead of triggering iterative `SELECT COUNT(*)` lookups for each category (e.g., when generating boss stats based on dynamic category sizes).
**Action:** Always identify opportunities to batch aggregate queries using `GROUP BY` when a list of items requires individual counts or calculations, and pass the precomputed data to helper functions.
