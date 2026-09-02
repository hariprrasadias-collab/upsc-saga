# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2025-02-05 - Optimize N+1 Query in Analytics
**Learning:** The `get_subject_wise` analytics endpoint used a loop that executed 18 individual SQL queries (3 per subject across 6 subjects) via `get_subject_performance`.
**Action:** Always batch related SQL queries using `GROUP BY` before looping. Refactored to fetch mock test averages, answer averages, and syllabus stats for all subjects using exactly 3 grouped queries, mapping the results in memory.
