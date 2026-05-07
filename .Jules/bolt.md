# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2026-05-06 - [Optimized XP history to eliminate N+1 queries]
**Learning:** The `consult_the_seer` function in `backend/app/routes/seer.py` was executing a separate SQL query to calculate the sum of XP for each day in a 7-day loop.
**Action:** Transformed the loop into a single bounded query (`WHERE due_date >= ? AND due_date <= ?`) with a `GROUP BY due_date`, mapping the results to a local Python dictionary for O(1) lookups. Ensure `NULL` values from `SUM()` are explicitly handled.
