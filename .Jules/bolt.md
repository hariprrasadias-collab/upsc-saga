# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2026-08-21 - [Eliminate N+1 queries in subject-wise analytics]
**Learning:** The `get_subject_wise` endpoint in `backend/app/routes/analytics.py` iteratively fetched `get_subject_performance` which executed three SQL queries for each subject. Inside loops, this triggers an N+1 query problem.
**Action:** Refactor the queries to run outside the loop using `GROUP BY` to fetch all necessary data in a single database round-trip for each metric, mapping the results into memory for fast lookup.
