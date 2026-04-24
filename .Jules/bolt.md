# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-03-03 - [Optimized boss stats generation to eliminate N+1 queries]
**Learning:** The `get_available_bosses` function in `backend/app/routes/arena.py` was iterating over a list of unique years and subjects to generate boss stats, executing a `COUNT(*)` database query inside the loop for each item (N+1 query problem). This O(N) database query pattern caused significant slowdowns. By executing a single `SELECT ..., COUNT(*) ... GROUP BY ...` query to aggregate counts upfront, we transformed an O(N) database query scenario into O(1).
**Action:** When iterating over distinct database records to calculate their associated counts or aggregates, use a single `GROUP BY` query to fetch all required aggregates at once, completely eliminating N+1 queries.
