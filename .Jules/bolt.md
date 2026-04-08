# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2024-05-23 - [Optimized boss category loading to eliminate N+1 queries]
**Learning:** The `/bosses` endpoint iteratively fetched question counts for each year and subject using `SELECT COUNT(*)`. This created an N+1 query loop when loading available arena bosses.
**Action:** Precompute category counts using a single `GROUP BY` database query and pass the values downstream via `precomputed_count` parameters to avoid redundant iterative SQL lookups.
