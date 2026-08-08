# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2025-03-04 - [Bulk Query Optimization for Subject Performance Analytics]
**Learning:** The `/api/analytics/subject-wise` route suffered from the N+1 query problem by iteratively calling `get_subject_performance` for each of the 6 subjects, resulting in 18 distinct queries (3 per subject).
**Action:** Replaced iterative queries with a single bulk query operation using the `IN` clause (`get_bulk_subject_performance`), significantly reducing the query overhead from O(N) to O(1).
