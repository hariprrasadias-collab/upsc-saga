# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-03-03 - [Optimized subject-wise analytics to eliminate N+1 queries]
**Learning:** The `get_subject_wise` endpoint in `backend/app/routes/analytics.py` iteratively executed database queries for each subject using a `for subject in subjects:` loop, executing multiple queries per iteration.
**Action:** Replaced the loop with a batched database query using `IN (...)` and `GROUP BY subject`, collecting the results into a Python map to return all subjects' performance stats in a single, batched O(1) query set instead of O(N).
