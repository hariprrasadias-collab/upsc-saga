# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2024-05-22 - [Optimize subject-wise analytics performance]
**Learning:** The `get_subject_wise` endpoint in `backend/app/routes/analytics.py` iteratively called `get_subject_performance` for each subject, resulting in an N+1 query pattern where 3 database queries were executed per subject in the loop.
**Action:** Lift the loop execution into a single helper function `get_all_subject_performances` utilizing an `IN` clause with a `GROUP BY` statement to batch the operations and resolve the bottleneck (18 DB calls to 3 DB calls for subject-wise analytics).
