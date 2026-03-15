# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2026-03-15 - [N+1 Query Issue in `get_available_bosses`]
**Learning:** In `get_available_bosses`, fetching distinct years/subjects and then iterating over each row to call a function (`get_boss_stats`) that executes a `SELECT COUNT(*)` query leads to an N+1 query performance bottleneck. We can fetch precalculated counts using a `GROUP BY` query.
**Action:** When a method iterates over a result set to fetch additional counts from the database, aggregate the counts directly in the initial query using `GROUP BY` or pass a precalculated list, instead of firing individual count queries per iteration.
