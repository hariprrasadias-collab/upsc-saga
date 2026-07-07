# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-03-03 - [Eliminate N+1 queries in subject-wise analytics]
**Learning:** The analytics dashboard triggered N+1 queries when fetching performance metrics across multiple subjects, iteratively querying the database for each subject.
**Action:** Refactor N+1 queries by pulling the loop into a single bulk query with `GROUP BY` and `IN ()` clauses, reducing database round-trips from O(N) to O(1) while maintaining proper user isolation.
