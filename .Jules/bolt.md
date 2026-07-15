# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-03-03 - [Optimized subject performance tracking to eliminate N+1 queries]
**Learning:** The `get_subject_wise` endpoint originally fetched subject performance iteratively for 6 subjects, running 3 queries for each subject inside a loop (total 18 queries). The queries can be batched using `IN` and `GROUP BY` to retrieve stats for all subjects in just 3 queries.
**Action:** Always refactor iterative database queries inside loops into single bulk queries using `IN` clauses to reduce DB roundtrips and improve endpoint latency.
