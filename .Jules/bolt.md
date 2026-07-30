# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2026-07-30 - [Optimized subject-wise analytics to eliminate N+1 queries]
**Learning:** The `get_subject_wise` analytics route queried subject performance data in a loop, resulting in a series of N+1 database queries. Since each call queried the same tables but filtered to a single subject, this caused unnecessary database overhead.
**Action:** Replace looped individual fetches with a single bulk query using `IN` clauses and `GROUP BY` logic, ensuring independent tables are wrapped in isolated `try...except` blocks to maintain fault tolerance.
