# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2026-08-18 - Eliminate N+1 queries in seer API routes
**Learning:** Functions iterating through a list (like last 7 days or all years) often execute DB queries in a loop, causing N+1 queries which is an inefficient pattern in SQLite.
**Action:** Lift repeated query logic out of loops using `GROUP BY` across the entire required dataset range to fetch all necessary data in O(1) query operations.
