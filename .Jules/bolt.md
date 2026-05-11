# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2024-05-11 - Bulk Querying Subjects to Avoid N+1 Subqueries in Subject-wise Analytics
**Learning:** The `get_subject_wise` endpoint in `backend/app/routes/analytics.py` had a significant performance bottleneck due to an N+1 query problem. It iterated over a list of subjects, executing `get_subject_performance` for each one, which in turn executed 3 separate queries (mock tests, answers, and syllabus). By refactoring this into a bulk fetching strategy (`get_all_subject_performances`) that grouped the queries using `IN` clauses and `GROUP BY subject`, we consolidated 18 individual queries into just 3 optimized queries for 6 subjects.
**Action:** Always prefer a single query using an `IN` clause and `GROUP BY` alongside a local dictionary mapping when processing aggregates for a known list of dimensions (like subject areas).
