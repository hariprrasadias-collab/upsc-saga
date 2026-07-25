# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).
## 2025-02-12 - N+1 optimization in subject performance metrics
**Learning:** The `get_subject_performance` function executes 3 individual queries per subject. Over a 6-subject batch request (`/analytics/subject-wise`), this results in 18 sequential database queries. By refactoring this into a batch function using `IN ({placeholders})` and `GROUP BY`, the queries can be combined into exactly 3 batch operations, reducing database roundtrips by 83% (from 18 to 3 queries).
**Action:** When calculating performance metrics across multiple distinct subjects or entities, always lift the iteration into the SQL layer using `GROUP BY` and `IN` clauses to perform bulk retrieval, preventing N+1 bottlenecks at the application layer. Wrap each metric's query in isolated `try...except` blocks to preserve fault tolerance.
