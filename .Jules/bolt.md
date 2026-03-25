# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimization requires a holistic view of both frontend and backend.
**Action:** Always check for existing patterns and measure impact before and after changes.

## 2025-03-03 - [Optimized syllabus progress trend to eliminate N+1 queries]
**Learning:** The `get_progress_trend` function in `backend/app/routes/analytics.py` iteratively fetched `syllabus_topics` data `days + 1` times (via `SELECT COUNT(*)` queries). However, because the `syllabus_topics` table only tracks current topic status and lacks a historical tracking mechanism, these inner-loop queries always returned the same value.
**Action:** Lift repeated logic out of loops when the underlying data tables do not support historical/time-series filters, calculating the value once beforehand to transform an O(N) database query scenario into O(1).

## 2025-03-03 - [Optimized subject-wise analytics with bulk queries]
**Learning:** When fetching metrics for multiple distinct entities (like 6 academic subjects), iterating and calling individual `AVG/COUNT/SUM` queries per entity results in a severe N+1 query problem. In this case, 6 subjects * 5 metrics meant 30 individual queries per request.
**Action:** Use `IN (?, ?, ...)` clauses and `GROUP BY` to aggregate metrics in bulk. Crucially, when combining multiple independent metrics (Mock scores, Answer writing, Syllabus completion), isolate each metric's bulk query in its own `try...except` block so a failure in one table does not abort the retrieval of the rest.
