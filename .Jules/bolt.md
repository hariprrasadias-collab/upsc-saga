# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## $(date +%Y-%m-%d) - [Optimized subject-wise analytics to eliminate N+1 queries]
**Learning:** The get_subject_wise function in backend/app/routes/analytics.py iterated through 6 subjects, running 3 independent database queries (mock tests, answer writing, syllabus) for each subject sequentially (totaling 18 queries). This N+1 pattern caused significant latency on the dashboard.
**Action:** Replaced sequential loop queries with a single batch execution utility using IN clauses and GROUP BY to fetch all required metrics across multiple subjects at once, transforming O(N) database roundtrips into O(1).
