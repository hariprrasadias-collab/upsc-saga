# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2026-08-27 - [Optimize N+1 queries using GROUP BY]
**Learning:** Calling database functions inside loops (e.g. iterating over subjects to fetch performance stats) leads to N+1 query problems which degrade API performance.
**Action:** When calculating statistics across multiple categories (like subjects), formulate a single bulk query using the `IN` clause and `GROUP BY`, then map the results in memory to avoid redundant database round-trips.
