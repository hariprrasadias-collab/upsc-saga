# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2024-06-22 - [Optimized subject wise analytics to eliminate N+1 queries]
**Learning:** The `get_subject_wise` route in `backend/app/routes/analytics.py` fetched subject performance statistics by iterating over subjects and calling `get_subject_performance`, which caused repeated individual SQL queries (N+1 bottleneck).
**Action:** Replaced the iterative database calls by aggregating the list of subjects and executing grouped queries using `WHERE ... IN ...` clauses to fetch metrics for all subjects in a single database pass, mapping the results back locally.
