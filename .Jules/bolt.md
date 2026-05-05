# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-03-04 - [Optimized get_available_bosses to eliminate N+1 queries]
**Learning:** In `backend/app/routes/arena.py`, the `get_available_bosses` route was fetching all unique years and subjects first, and then firing off a separate `SELECT COUNT(*)` query for each one inside the loop via `get_boss_stats`.
**Action:** By modifying `get_available_bosses` to fetch the count directly alongside the distinct values via a single `GROUP BY` query, and modifying `get_boss_stats` to accept this pre-calculated count, we eliminated the N+1 query overhead.
