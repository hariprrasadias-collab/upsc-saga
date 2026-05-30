# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2024-05-24 - N+1 query issue in get_subject_wise endpoint
**Learning:** Found an N+1 query issue in the `/api/analytics/subject-wise` endpoint where we looped through 6 subjects and executed 3 queries for each subject.
**Action:** Created `get_all_subject_performances` to execute 3 bulk `GROUP BY subject` queries, wrapping each in an exception handler so missing tables don't crash other metrics.
